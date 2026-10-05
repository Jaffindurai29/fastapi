# 12/g — Encrypting fields with Fernet, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md). No login here: the
point is what happens to a value between the request and the database.

1. **Hashing vs encryption vs encoding.** Three things that all turn
   text into unreadable-looking text, for very different reasons:

   | | Reversible? | Needs a key? | Use it for | Example |
   |---|---|---|---|---|
   | **Hashing** | No (one-way) | No | Checking a value without storing it: passwords | `pwdlib` / Argon2 in [12/a](../a/STEPS.md) |
   | **Encryption** | Yes (two-way) | Yes, secret | Storing a value you must read back: phone, address, API tokens | Fernet, this lesson |
   | **Encoding** | Yes, by anyone | No | Making bytes safe to transport. **Not security** | Base64, URL encoding, the JWT payload in [12/b](../b/STEPS.md) |

   A password is hashed because the server never needs it back, only to
   compare it. A phone number is encrypted because support staff need to
   call it. Base64 hides nothing: anyone can decode it.

2. **`config.py` — the key.**

   ```python
   DEV_FERNET_KEY = "BxL7roHgsuzl6NLf-j9jBB6LfGEdkbzrjzR1-0j24cA="

   FERNET_KEY = os.getenv("FERNET_KEY", DEV_FERNET_KEY)
   ```

   A Fernet key is 32 random bytes, base64-encoded. The fallback exists
   only so the lesson runs with zero setup, and the code says so loudly.
   That key is in git, so it protects nothing. Three rules for a real key:

   - **Keep it secret, keep it out of git.** It goes in `.env` (which is
     git-ignored) or a secrets manager. Anyone with the key and a database
     dump can read every encrypted column.
   - **Losing the key means losing the data.** There is no "forgot my
     key" recovery. Back it up somewhere safe, separately from the
     database backups (keeping both in one place defeats the point).
   - **Don't just change it.** Old rows were encrypted with the old key.
     See step 7 for how to rotate it properly.

3. **`encryption.py` — two small helpers.**

   ```python
   fernet = Fernet(FERNET_KEY)


   def encrypt(plaintext: str) -> str:
       return fernet.encrypt(plaintext.encode()).decode()


   def decrypt(ciphertext: str) -> str:
       return fernet.decrypt(ciphertext.encode()).decode()
   ```

   Fernet works on `bytes`, the database column holds `str`, hence the
   `.encode()` / `.decode()`. Fernet is AES encryption **plus** a
   signature (HMAC), so it's not just secret but tamper-proof. A wrong key
   or an edited value raises `InvalidToken` instead of silently returning
   garbage.

4. **`crud.py` — encrypt on the way in, `models.py` — `Text` columns.**

   ```python
   row = CustomerModel(
       name=customer.name,
       email=customer.email,
       phone_encrypted=encrypt(customer.phone),
       notes_encrypted=encrypt(customer.notes) if customer.notes is not None else None,
   )
   ```

   The plaintext phone never reaches the database, its logs or its
   backups. Ciphertext is much longer than the input (a short phone
   number becomes about 100 characters), so the columns are `Text`, not
   `String(30)`. The `_encrypted` suffix makes it obvious to the next
   developer that these columns can't be read directly.

5. **`main.py` — decrypt on the way out.**

   ```python
   def to_out(row: CustomerModel) -> CustomerOut:
       return CustomerOut(
           id=row.id,
           name=row.name,
           email=row.email,
           phone=decrypt(row.phone_encrypted),
           notes=decrypt(row.notes_encrypted) if row.notes_encrypted is not None else None,
       )
   ```

   `CustomerOut` has `phone`, the row has `phone_encrypted`, so
   `from_attributes` (see [8/d](../../8/d)) can't map them by itself. We
   build the output explicitly. The `/raw` route *can* use
   `from_attributes` (`CustomerRawOut`), because its fields match the
   columns. That route exists only so you can see the ciphertext. A real
   app must never return encrypted columns (or have a route like it).

6. **Same plaintext, different ciphertext every time.** Fernet mixes a
   random IV and a timestamp into every encryption. So
   `encrypt("555-0100")` gives a new result each call (try the
   "Try this too" in the README). That's good, because an attacker can't
   spot customers sharing a phone number. But it means **you can't
   search encrypted columns**:

   ```python
   # Never matches: the stored value was encrypted with a different IV.
   db.query(CustomerModel).filter(CustomerModel.phone_encrypted == encrypt("555-0100"))
   ```

   No `WHERE`, no `ORDER BY`, no unique index on them. If you need "find
   the customer with this phone", add a second column that stores a
   **keyed hash** of the normalised value
   (`hmac.new(key, phone.encode(), "sha256").hexdigest()`), which *is*
   the same every time, and search on that. That's also why `name` and
   `email` here stay plain text: only encrypt what you never search by.

7. **A wrong key is a server error, and it gets a clear log line.**

   ```python
   @app.exception_handler(InvalidToken)
   def invalid_token_handler(request: Request, exc: InvalidToken):
       logger.error(
           "Could not decrypt a stored value on %s %s. Is FERNET_KEY the key the "
           "data was encrypted with?",
           request.method,
           request.url.path,
       )
       return JSONResponse(status_code=500, content={"detail": "Could not decrypt stored data"})
   ```

   The client did nothing wrong, so it's a `500`, not a `4xx`. The
   response says nothing useful to an attacker. The log tells **you**
   the likely cause (a changed or missing `FERNET_KEY`). Custom handlers
   were introduced in [8/c](../../8/c/STEPS.md).

8. **Key rotation with `MultiFernet` (not implemented here).** To
   replace a key without losing data, list the **new** key first and keep
   the old one for reading:

   ```python
   from cryptography.fernet import Fernet, MultiFernet

   fernet = MultiFernet([Fernet(NEW_KEY), Fernet(OLD_KEY)])

   fernet.encrypt(b"...")      # always uses NEW_KEY
   fernet.decrypt(token)       # tries NEW_KEY, then OLD_KEY
   fernet.rotate(token)        # decrypts with whichever works, re-encrypts with NEW_KEY
   ```

   Deploy that, run a one-off script that calls `rotate()` on every
   encrypted column and saves the result, and once every row is done,
   remove `OLD_KEY`.

9. **Optional: automatic encryption with a `TypeDecorator`.** Instead of
   calling `encrypt()`/`decrypt()` by hand, SQLAlchemy can do it for every
   read and write of a column:

   ```python
   from sqlalchemy.types import Text, TypeDecorator


   class EncryptedText(TypeDecorator):
       impl = Text
       cache_ok = True

       def process_bind_param(self, value, dialect):      # Python -> DB
           return None if value is None else encrypt(value)

       def process_result_value(self, value, dialect):    # DB -> Python
           return None if value is None else decrypt(value)


   phone = Column(EncryptedText, nullable=False)  # row.phone is plain text in Python
   ```

   Less code in routes and impossible to forget, but also invisible:
   someone reading `row.phone` may not realise it's encrypted at rest.
   This lesson keeps the explicit helpers so you can see each step.
