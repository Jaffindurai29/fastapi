# 12/b — JWT login, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md) and the same hashing as
[12/a](../a/STEPS.md). New here: `config.py`, tokens in `security.py`,
and the OAuth2 login form.

1. **Why a token at all.** HTTP forgets you between requests. Without a
   token, the client would send the password on every call. Instead it
   sends the password **once** to `POST /token` and gets back a signed
   token that says "this is alice, until 10:15". Every later request
   carries the token, and the server only has to check the signature,
   no database lookup of the password.

2. **What a JWT looks like:** three base64url chunks joined by dots,
   `header.payload.signature`:

   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTc5MTE5Njc3NSwidHlwZSI6ImFjY2VzcyJ9.NsiOoyiFzply8_zi-_4uHbrN66UwKP3twAZ6mv1BYPo
   ```

   - **header**: `{"alg": "HS256", "typ": "JWT"}`, how it was signed
   - **payload**: `{"sub": "alice", "exp": 1791196775, "type": "access"}`, the claims
   - **signature**: HMAC-SHA256 of the first two parts, using `SECRET_KEY`

3. **Base64 is not encryption.** The header and payload are only
   encoded, so anyone holding the token can read them. `/token/inspect`
   proves it, decoding with no key at all:

   ```python
   header = jwt.get_unverified_header(token)
   payload = jwt.decode(token, options={"verify_signature": False})
   ```

   So **never put secrets in the payload**: no passwords, no hashes, no
   card numbers. A username and an expiry are fine. (Real code only uses
   `verify_signature: False` for debugging, never to decide access.)

4. **The signature proves nobody tampered with it.** Change one
   character of the payload (say `"sub": "alice"` → `"admin"`) and the
   signature no longer matches, because only someone who knows
   `SECRET_KEY` can compute a matching one. `/token/inspect` runs the
   real check right after:

   ```python
   try:
       verified = decode_token(token)
       return {"header": header, "payload": payload, "valid": True, "verified_payload": verified}
   except jwt.InvalidTokenError as exc:
       return {"header": header, "payload": payload, "valid": False, "error": str(exc)}
   ```

   A tampered token comes back `"valid": false` with `"Signature
   verification failed"`, even though its payload reads `admin`.

5. **`config.py` — one secret, from the environment:**

   ```python
   SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me-in-production-0123456789")
   ALGORITHM = "HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
   REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
   ```

   Whoever knows `SECRET_KEY` can mint a token for any user, so it lives
   in `.env` (never in git) and should be long and random:
   `python -c "import secrets; print(secrets.token_hex(32))"`. The
   default is fine on your laptop, but it's public (it's in this repo),
   so never use it anywhere real. PyJWT prints an
   `InsecureKeyLengthWarning` if a key is shorter than 32 bytes. Changing the
   key logs everybody out, since old tokens stop verifying.
   `REFRESH_TOKEN_EXPIRE_DAYS` is used from [12/d](../d/STEPS.md).

6. **`security.py` — making a token:**

   ```python
   def create_access_token(username: str, expires_delta: timedelta | None = None) -> str:
       if expires_delta is None:
           expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
       payload = {
           "sub": username,  # who the token is about (the "subject")
           "exp": datetime.now(timezone.utc) + expires_delta,  # stored as a Unix timestamp
           "type": "access",
       }
       return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
   ```

   `sub` and `exp` are standard JWT claim names. `type` is ours; it
   separates access tokens from the refresh tokens of
   [12/d](../d/STEPS.md). `expires_delta` is a parameter so tests can
   make an already-expired token.

7. **`exp`: tokens die on their own.** A stolen token is a stolen login,
   so it should be short-lived. `jwt.decode` rejects it once `exp` has
   passed:

   ```python
   def decode_token(token: str) -> dict:
       return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
   ```

   It raises `jwt.ExpiredSignatureError` for an expired token and
   `jwt.InvalidTokenError` (its parent class) for anything else wrong.
   `algorithms=[ALGORITHM]` is a whitelist. Never trust the `alg` in the
   token's own header; a classic attack sets it to `none`.

8. **`main.py` — the login form:**

   ```python
   @app.post("/token", response_model=Token,
             responses={401: {"description": "Incorrect username or password"}})
   def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
       user = crud.authenticate(db, form_data.username, form_data.password)
       if user is None:
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Incorrect username or password",
               headers={"WWW-Authenticate": "Bearer"},
           )
       return {"access_token": create_access_token(user.username), "token_type": "bearer"}
   ```

   `OAuth2PasswordRequestForm` reads **form fields** `username` and
   `password`, because that's what the OAuth2 "password flow" spec says.
   Following the spec is what lets the "Authorize" button in `/docs` log
   in for you in [12/c](../c/STEPS.md). Reading forms needs the
   `python-multipart` package. The response keys `access_token` and
   `token_type: "bearer"` are fixed by the same spec. The `401` is the
   same for a missing user and a wrong password, as in
   [12/a](../a/STEPS.md) step 6.

9. **`models.py` — one table for the rest of the topic.** `sec_users`
   adds `is_active` and is shared by 12/b, 12/c, 12/d and 12/i, so the
   model is identical in all four. `carol` is seeded with
   `is_active=False`. She can still get a token here; [12/c](../c/STEPS.md)
   is where that's checked.

10. **What's missing: anything that uses the token.** There are no
    protected routes yet. [12/c](../c/STEPS.md) adds a dependency that
    reads `Authorization: Bearer <token>`, verifies it, and loads the
    user.
