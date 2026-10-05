# 12/j — The security checklist, step by step

12/a–12/i each taught one idea on its own. This app uses all of them at
once, so instead of walking file by file, this walkthrough goes item by
item down a **security checklist**: what the rule is, where it lives in
the code, and why it's there. Every item is also marked with a
`# CHECKLIST:` comment in the code, so you can `grep CHECKLIST` to find
them all.

## Part 1 — Who are you? (authentication)

1. **Passwords are hashed, never stored.** (`security.py`, as in
   [12/a](../a/STEPS.md))

   ```python
   password_hash = PasswordHash.recommended()


   def hash_password(password: str) -> str:
       return password_hash.hash(password)
   ```

   The `secure_users` table only has a `hashed_password` column.
   Argon2 is slow on purpose and salts every hash, so a leaked database
   doesn't hand out passwords. `UserCreate.password` also has
   `max_length=128`, so nobody can make the hasher chew on a 10 MB
   string.

2. **Generic login error.** (`routers/auth.py`)

   ```python
   user = crud.get_user_by_username(db, form.username)
   # Hash-check even when the user doesn't exist, so both failures take
   # the same time.
   password_ok = verify_password(form.password, user.hashed_password if user else DUMMY_HASH)
   # CHECKLIST: generic login error. "No such user" vs "wrong password"
   # would tell an attacker which usernames exist.
   if user is None or not password_ok or not user.is_active:
       raise credentials_error("Incorrect username or password")
   ```

   **Why:** "No such user" and "Wrong password" are two different
   answers, and that difference tells an attacker which usernames are
   real. The same goes for timing: checking an Argon2 hash takes tens of
   milliseconds, and returning early for an unknown user would be noticeably
   faster. Checking against `DUMMY_HASH` makes both paths take the same
   time.

3. **Rate-limited login.** (`rate_limit.py`, `routers/auth.py`, `main.py`,
   as in [12/i](../i/STEPS.md))

   ```python
   @router.post("/token", response_model=Token)
   @limiter.limit(settings.login_rate_limit)
   def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
   ```

   ```python
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

   **Why:** without a limit, a script can try thousands of passwords a
   minute. With `5/minute` per IP, the 6th try gets `429 Too Many
   Requests`, even with the right password. `@limiter.limit` must sit
   **below** `@router.post`, and the function must take a `request:
   Request` argument, because slowapi reads the client IP from it. The
   limit itself comes from settings (`LOGIN_RATE_LIMIT`), so production
   can tune it without a code change.

4. **Short-lived access tokens, refresh tokens for the rest.**
   (`config.py`, `security.py`, as in [12/b](../b/STEPS.md) and
   [12/d](../d/STEPS.md))

   ```python
   access_token_expire_minutes: int = 15
   refresh_token_expire_days: int = 7
   ```

   **Why:** an access token can't be "logged out": once issued, it's
   valid until `exp`. Keeping it to 15 minutes caps the damage if one
   leaks. The refresh token lasts longer but is only ever sent to one
   route (`/refresh`), never with every request.

5. **Token type is checked.** (`security.py`)

   ```python
   # A refresh token must not work as an access token, and vice versa.
   if payload.get("type") != expected_type or not payload.get("sub"):
       raise credentials_error()
   ```

   **Why:** both tokens are signed with the same key, so the signature
   alone can't tell them apart. Without this check, a 7-day refresh
   token would work as a 7-day access token, and the "short-lived"
   rule from item 4 would be meaningless.

6. **The algorithm is fixed by the server.** (`security.py`)

   ```python
   payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[ALGORITHM])
   ```

   **Why:** a JWT's header says which algorithm it uses, and the token
   is attacker-controlled. `algorithms=[...]` means the server only
   accepts HS256, so a token claiming `"alg": "none"` (no signature at
   all) is rejected.

7. **Refresh tokens rotate.** (`models.py`, `routers/auth.py`)

   ```python
   stored = crud.get_refresh_token(db, payload.get("jti", ""))
   # Rotation: each refresh token works exactly once. Reusing an old one
   # (e.g. a stolen copy) fails here.
   if stored is None or stored.revoked:
       raise credentials_error("Refresh token is no longer valid")
   ...
   crud.revoke_refresh_token(db, stored)
   return issue_tokens(db, user)
   ```

   **Why:** a JWT is valid until it expires. Nothing about the token
   itself can "use it up". So each refresh token carries a random
   `jti`, and the `secure_refresh_tokens` table remembers which ones
   have been used. `/refresh` hands back a **new pair** and marks the
   old one revoked. If someone steals a refresh token, they get one use
   at most, and the real user's next refresh fails, which is a signal
   something is wrong.

## Part 2 — What may you do? (authorization)

8. **Role re-read from the database, not trusted from the token.**
   (`dependencies.py`)

   ```python
   payload = decode_token(token, expected_type="access")
   # CHECKLIST: the role is re-read from the database on every request,
   # never trusted from the token. Demote or deactivate a user and it
   # takes effect immediately, not when their token expires.
   user = crud.get_user_by_username(db, payload["sub"])
   ```

   **Why:** the token only says *who* you are (`sub`). If it also said
   `"role": "admin"`, demoting someone would do nothing until their
   token expired. One small query per request buys you instant
   demotion and instant deactivation (`is_active=False` → `403`).

9. **Role checks return `403`.** (`dependencies.py`, as in
   [12/e](../e/STEPS.md))

   ```python
   def require_role(role: str):
       def checker(user: UserModel = Depends(get_current_user)) -> UserModel:
           if user.role != role:
               raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
           return user

       return checker
   ```

   ```python
   @router.get("/admin/users", response_model=list[UserOut])
   def list_users(db: Session = Depends(get_db), admin: UserModel = Depends(require_role("admin"))):
   ```

   `401` means "I don't know who you are". `403` means "I know exactly
   who you are, and the answer is no." Logging in again won't help a
   `403`, so the frontend should show a message, not a login form.

10. **Ownership checks on every note route.** (`routers/notes.py`, as in
    [12/f](../f/STEPS.md))

    ```python
    def get_owned_note(db: Session, note_id: int, user: UserModel) -> NoteModel:
        """Load a note and check the current user may touch it."""
        note = crud.get_note(db, note_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        # Ownership check: logged in is not enough, it has to be YOUR note.
        # Admins may act on any note.
        if note.owner_id != user.id and user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't own this note")
        return note
    ```

    **Why:** "is logged in" is not the same as "may read note 3". Ids
    are easy to guess (1, 2, 3...), so without this check Alice could
    read Bob's notes just by changing the number in the URL. GET, PUT
    and DELETE all go through this one function, so none of them can
    forget the check.

11. **The client never picks its owner or role.** (`crud.py`,
    `schemas.py`)

    ```python
    def create_note(db: Session, data: NoteCreate, owner_id: int) -> NoteModel:
        # owner_id comes from the logged-in user, never from the request body.
        row = NoteModel(**data.model_dump(), owner_id=owner_id)
    ```

    `NoteCreate` has no `owner_id`, and `UserCreate` has no `role`.
    Sending `{"role": "admin"}` to `/register` is silently ignored, and
    the new user is always `"user"`. This mistake is called **mass
    assignment**: copying whatever the client sent straight into the
    database row.

## Part 3 — What leaves the server?

12. **`response_model` never exposes `hashed_password`.** (`schemas.py`)

    ```python
    # CHECKLIST: response_model never exposes hashed_password. It simply
    # isn't listed here, so it can't leave the server even by accident.
    class UserOut(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        username: str
        role: str
        is_active: bool
    ```

    `/users/me` returns the full ORM row, hash and all, and `UserOut`
    filters it down. Same trick as [8/d](../../8/d) with
    `supplier_cost`. A hash isn't the password, but it lets an attacker
    guess offline at full speed, with no rate limit.

13. **Nothing secret in the JWT payload.** (`security.py`)

    ```python
    # Note what is NOT in here: no role, no password, nothing secret.
    # Anyone holding the token can base64-decode and read the payload.
    ```

    A JWT is **signed**, not **encrypted**. Paste one into jwt.io and
    you can read it. The signature only proves nobody changed it.

## Part 4 — Configuration and deployment

14. **Secrets come from the environment.** (`config.py`)

    ```python
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)
    ...
    secret_key: SecretStr = SecretStr(DEV_SECRET_KEY)
    ```

    `Settings` reads each field from the env var of the same name
    (`SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, ...) or from `.env`.
    `SecretStr` prints as `'**********'`, so the key can't end up in a
    log by accident, and `hide_input_in_errors=True` keeps it out of
    error messages too. The real value is only read where it's needed:
    `settings.secret_key.get_secret_value()` in `security.py`.

15. **Production refuses to start with a weak secret.** (`config.py`)

    ```python
    @model_validator(mode="after")
    def check_production_secret(self) -> "Settings":
        if self.is_production:
            key = self.secret_key.get_secret_value()
            if key == DEV_SECRET_KEY:
                raise ValueError("SECRET_KEY must be set in production (the dev default is public)")
            if len(key) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return self
    ```

    **Why:** the dev key is printed right here in a public repo. Anyone
    who knows it can sign their own token saying `"sub": "admin"`.
    Forgetting to set `SECRET_KEY` is an easy mistake, so the app makes
    it impossible to deploy that way: `settings = Settings()` runs when
    `config.py` is imported, the validator raises, and uvicorn never
    starts. Crashing loudly at startup is much better than running
    quietly with a public key.

16. **No `/docs` in production.** (`main.py`)

    ```python
    docs_off = settings.is_production
    app = FastAPI(
        title="Secure notes",
        docs_url=None if docs_off else "/docs",
        redoc_url=None if docs_off else "/redoc",
        openapi_url=None if docs_off else "/openapi.json",
    )
    ```

    **Why:** `/openapi.json` is a complete map of every route, every
    parameter and every error. Handy while building, but in production
    there's no reason to give strangers that map. Turning off
    `openapi_url` matters most: `/docs` and `/redoc` both load it.
    This is defense in depth, not a lock. The routes are still
    protected by the checks above either way.

17. **CORS only from settings.** (`main.py`)

    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    ```

    Compare [7/a](../../7/a), which hard-coded the origins and allowed
    every method and header. Here the list comes from `CORS_ORIGINS`,
    so production can list its real frontend domain. **Never**
    `allow_origins=["*"]` with `allow_credentials=True`: that would let
    any website make logged-in requests on a visitor's behalf (and
    browsers refuse that combination anyway). This app sends tokens in
    the `Authorization` header, not in cookies, so it doesn't need
    credentials at all.

18. **Security headers on every response.** (`main.py`)

    ```python
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        # Don't let the browser guess a different content type than we sent.
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Don't allow this API to be framed by another site (clickjacking).
        response.headers["X-Frame-Options"] = "DENY"
        # Don't leak our URLs (which might contain ids) to other sites.
        response.headers["Referrer-Policy"] = "no-referrer"
        return response
    ```

    `@app.middleware("http")` wraps **every** request, including `401`s
    and `404`s: run the route (`call_next`), then add headers to
    whatever came back. These three headers cost nothing and close off
    whole classes of browser tricks. A real deployment usually adds
    `Strict-Transport-Security` too, once it's served over HTTPS (often
    by the reverse proxy rather than the app).

## Not in this app (but on a real checklist)

- **HTTPS.** Tokens and passwords travel in plain text over HTTP. In
  production, always put the app behind HTTPS.
- **Encrypting sensitive fields** at rest: see [12/g](../g/STEPS.md).
- **Hiding sequential ids** in URLs: see [12/h](../h/STEPS.md). This
  app keeps plain ids because the ownership check (item 10) is the
  real protection. Hiding ids only makes guessing harder.
- **A shared rate-limit store** (Redis) when running more than one
  server process. The in-memory count in `rate_limit.py` is per process.
