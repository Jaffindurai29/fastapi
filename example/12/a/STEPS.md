# 12/a — Password hashing, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md). New here: `security.py`
and the idea that the server should never be able to read a user's
password, not even its own stored copy.

1. **Hashing is not encryption.** Encryption is two-way: with the key
   you get the original back. A hash is **one-way**: you can turn
   `"alice-password"` into a hash, but nothing turns the hash back into
   `"alice-password"`, so it cannot be decrypted. To check a login you
   hash the attempt the same way and compare. If the database leaks,
   the attacker gets hashes, not passwords, and has to guess each
   password one by one.

2. **Never store plain text.** People reuse passwords. A leaked table of
   plain-text passwords is also a leaked set of email and bank logins.
   That's why `models.py` has no `password` column at all:

   ```python
   username = Column(String(30), nullable=False, unique=True)
   # Only the HASH is stored. There is no "password" column at all.
   # 255 leaves room: an Argon2 hash is ~97 characters.
   hashed_password = Column(String(255), nullable=False)
   ```

3. **`security.py` — `pwdlib` with Argon2:**

   ```python
   from pwdlib import PasswordHash

   password_hash = PasswordHash.recommended()


   def hash_password(password: str) -> str:
       return password_hash.hash(password)


   def verify_password(password: str, hashed: str) -> bool:
       return password_hash.verify(password, hashed)
   ```

   `PasswordHash.recommended()` picks Argon2 with safe settings. Older
   FastAPI tutorials use `passlib` with bcrypt. `passlib` is no longer
   maintained and breaks on Python 3.13+, so use `pwdlib`.

4. **Why a slow algorithm, not SHA-256.** SHA-256 is built to be
   **fast**: a graphics card can try billions of guesses per second
   against a SHA-256 hash. Argon2 and bcrypt are built to be **slow and
   memory-hungry** on purpose. One login takes a fraction of a second,
   which nobody notices, but billions of guesses become impractical. The
   cost settings are stored inside the hash itself:

   ```
   $argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
   ```

   `m=65536` is 64 MB of memory per hash, `t=3` is three passes. You
   can raise them later and old hashes still verify, because each one
   carries its own settings.

5. **Salt: why the same password hashes differently.** Every call to
   `hash()` mixes in a fresh random **salt** (the part before the last
   `$`) and stores it inside the result. `GET /hash-demo` shows it:

   ```python
   first = hash_password(password)
   second = hash_password(password)
   return {
       "password": password,
       "hash_1": first,
       "hash_2": second,
       "hashes_equal": first == second,
       "verify_hash_1": verify_password(password, first),
       "verify_hash_2": verify_password(password, second),
       "verify_wrong_password": verify_password(password + "x", first),
   }
   ```

   `hashes_equal` is `false`, yet both verify. Without a salt, every
   user with the password `123456` would have the same hash, so cracking
   one cracks them all, and attackers could use pre-computed lookup
   tables ("rainbow tables"). With a salt, each hash has to be attacked
   on its own. `verify()` reads the salt back out of the stored hash, so
   you never store it separately.

6. **`crud.py` — hash on the way in, verify on login:**

   ```python
   def create_user(db: Session, username: str, password: str) -> UserModel:
       # Hash BEFORE it touches the database. The plain password is
       # never stored, logged, or returned.
       row = UserModel(username=username, hashed_password=hash_password(password))
       ...


   def authenticate(db: Session, username: str, password: str) -> UserModel | None:
       user = get_user_by_username(db, username)
       if user is None:
           return None
       if not verify_password(password, user.hashed_password):
           return None
       return user
   ```

   `authenticate` returns `None` for both failures, and `main.py` turns
   both into the **same** `401`:

   ```python
   raise HTTPException(
       status_code=status.HTTP_401_UNAUTHORIZED,
       detail="Incorrect username or password",
       headers={"WWW-Authenticate": "Bearer"},
   )
   ```

   If the message said "user not found" in one case and "wrong password"
   in the other, anyone could find out which usernames exist (**user
   enumeration**) and then focus their guessing on those. The
   `WWW-Authenticate` header is what the HTTP spec expects on a `401`;
   it starts to matter once tokens arrive in [12/b](../b/STEPS.md).
   (A patient attacker could still time the two cases, since a missing
   user skips the slow `verify`. Some production code verifies against a
   dummy hash to even that out.)

7. **`schemas.py` — the hash never leaves the server.** `/register` and
   `/users` use `response_model=UserOut`, which has only `id` and
   `username`, the same trick as [8/d](../../8/d):

   ```python
   class UserOut(BaseModel):
       model_config = ConfigDict(from_attributes=True)

       id: int
       username: str
   ```

   A hash is not a password, but it's exactly what an attacker would
   crack offline, so it stays in the database.

8. **`409` for a taken username.** `/register` checks first, the same
   way [8/b](../../8/b) handles duplicate item names, and the
   `unique=True` column is the last line of defence.

9. **What's missing: staying logged in.** `/login` says "yes, that's
   right" and nothing more. The next request knows nothing about it, so
   the client would have to send the password every time.
   [12/b](../b/STEPS.md) replaces the success message with a signed
   token.
