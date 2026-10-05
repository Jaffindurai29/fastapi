# 12/c — Protected routes, step by step

`database.py`, `models.py`, `config.py`, `security.py` and `crud.py`
are the same as [12/b](../b/STEPS.md). New here: `dependencies.py`, and
routes that use it.

1. **How the client sends the token.** Every request to a locked route
   carries one header:

   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
   ```

   "Bearer" means "whoever bears (holds) this token is let in", which is
   exactly why a stolen token is as good as a stolen password until it
   expires.

2. **`dependencies.py` — `OAuth2PasswordBearer` pulls the token out:**

   ```python
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
   ```

   As a dependency it returns the part after `Bearer `. If the header is
   missing (or uses another scheme, like `Basic`), it answers `401 Not
   authenticated` by itself, before your code runs. `tokenUrl="token"`
   does not check anything; it tells `/docs` where the **Authorize**
   button should send the username and password. That's why login had to
   be an OAuth2 form at `POST /token` in [12/b](../b/STEPS.md).

3. **`get_current_user` — from token to user row:**

   ```python
   def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
       try:
           payload = decode_token(token)
       except jwt.ExpiredSignatureError:  # subclass, so it must come first
           raise credentials_error("Token has expired")
       except jwt.InvalidTokenError:  # bad signature, garbage, wrong algorithm...
           raise credentials_error()

       if payload.get("type") != "access":
           raise credentials_error()

       username = payload.get("sub")
       user = crud.get_user_by_username(db, username) if username else None
       if user is None:  # valid token, but the account was deleted since
           raise credentials_error()
       return user
   ```

   Four checks, in order:
   - **signature + expiry**: `decode_token` from 12/b. `ExpiredSignatureError`
     is a subclass of `InvalidTokenError`, so it has to be caught first
     or the general handler would swallow it.
   - **type**: only `"access"` tokens open doors. In [12/d](../d/STEPS.md)
     a long-lived refresh token must not work here.
   - **sub**: a token can be perfectly signed and still name a user who
     no longer exists.
   - **load the user** so routes get a real row, with fresh data.

   Every failure is the same `401` with `WWW-Authenticate: Bearer`, the
   header the HTTP spec expects with a `401`. Saying *why* a token is
   bad helps attackers more than users, so the only distinct message is
   "Token has expired", which tells an honest client to log in again.

4. **`get_current_active_user` — a dependency on a dependency:**

   ```python
   def get_current_active_user(user: UserModel = Depends(get_current_user)) -> UserModel:
       if not user.is_active:
           # 403, not 401: we know exactly who this is, and the answer is no.
           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
       return user
   ```

   **`401` vs `403`:** `401 Unauthorized` really means *unauthenticated*:
   "I don't know who you are, send valid credentials". `403 Forbidden`
   means "I know who you are, and you're not allowed". `carol`'s token
   is valid, so logging in again wouldn't help; that's a `403`. (The
   official FastAPI tutorial uses `400` here; `403` is the more precise
   code.) Splitting the check into two dependencies means a route that
   should accept deactivated users (say, "reactivate my account") can
   depend on `get_current_user` instead.

5. **`main.py` — locking a route is one parameter:**

   ```python
   @app.get("/users/me", response_model=UserOut, responses=AUTH_ERRORS)
   def read_me(current_user: UserModel = Depends(get_current_active_user)):
       return current_user


   @app.get("/items", responses=AUTH_ERRORS)
   def list_items(current_user: UserModel = Depends(get_current_active_user)):
       return ITEMS
   ```

   If the dependency raises, the route body never runs. If it returns,
   `current_user` is a real, active user with a valid token. `/items`
   doesn't even use `current_user`; asking for it is enough to lock the
   route. `/public` has no such parameter, so it stays open.
   `response_model=UserOut` keeps `hashed_password` out of `/users/me`,
   as in [12/a](../a/STEPS.md).

6. **Why `/users/me` and not `/users/{id}`.** The token already says who
   you are. A `/users/{id}` route would have to check that `id` matches
   the token, and forgetting that check is a classic bug (any logged-in
   user reads anyone's data). Routes that act "as me" should take the
   user from the token, never from the URL.

7. **Testing the failure paths.** `create_access_token` takes an
   `expires_delta`, so a test can mint a token that's already expired:

   ```python
   expired = security.create_access_token("alice", timedelta(minutes=-1))
   c.get("/users/me", headers={"Authorization": f"Bearer {expired}"})  # 401 Token has expired
   ```

8. **What's missing: staying logged in.** After 15 minutes the token
   dies and the user has to type their password again. Making the token
   last a week would fix that, but a stolen token would then work for a
   week too. [12/d](../d/STEPS.md) solves it with a second, long-lived
   refresh token.
