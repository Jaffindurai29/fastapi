# 12/d — Refresh tokens, step by step

`database.py`, `models.py`, `config.py`, `crud.py` and `dependencies.py`
are the same as [12/c](../c/STEPS.md). New here: a second token type in
`security.py`, and `POST /refresh`.

1. **Why two tokens.** One token can't be both short-lived (so a stolen
   one is useless soon) and long-lived (so users don't type their
   password every 15 minutes). So we split the job:

   | | Access token | Refresh token |
   |---|---|---|
   | Lives | 15 minutes | 7 days |
   | Sent | on **every** API call | only to `POST /refresh` |
   | Opens | protected routes | nothing but `/refresh` |

   The access token is the one flying around constantly, in headers and
   logs, so it's the one most likely to leak, and it dies fast. The
   refresh token travels rarely and to one place only.

2. **`security.py` — the refresh token:**

   ```python
   def create_refresh_token(username: str, expires_delta: timedelta | None = None) -> str:
       if expires_delta is None:
           expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
       payload = {
           "sub": username,
           "exp": datetime.now(timezone.utc) + expires_delta,
           "type": "refresh",
           "jti": secrets.token_hex(16),
       }
       return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
   ```

   Same key, same algorithm, different `type`. `jti` ("JWT ID") is a
   standard claim for a unique token id. Here it just makes sure two
   refresh tokens issued in the same second are different strings. It's
   also what a denylist would store (step 7). `create_token_pair` builds
   the `{access_token, refresh_token, token_type}` response used by both
   login and `/refresh`.

3. **The `type` claim keeps them apart.** Both tokens are signed with
   the same `SECRET_KEY`, so both pass `decode_token`. Without a type
   check, a 7-day refresh token would open `/users/me` for a week,
   defeating the point. 12/c's `get_current_user` already demanded
   `"access"`:

   ```python
   if payload.get("type") != "access":
       raise credentials_error()
   ```

   and `/refresh` demands the opposite:

   ```python
   if payload.get("type") != "refresh":
       raise credentials_error("Invalid refresh token")
   ```

4. **`main.py` — `POST /refresh`:**

   ```python
   @app.post("/refresh", response_model=TokenPair,
             responses={401: {"description": "Invalid or expired refresh token"}})
   def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
       try:
           payload = decode_token(body.refresh_token)
       except jwt.ExpiredSignatureError:
           raise credentials_error("Refresh token has expired")
       except jwt.InvalidTokenError:
           raise credentials_error("Invalid refresh token")

       if payload.get("type") != "refresh":
           raise credentials_error("Invalid refresh token")

       user = crud.get_user_by_username(db, payload.get("sub") or "")
       if user is None or not user.is_active:
           raise credentials_error("Invalid refresh token")

       return create_token_pair(user.username)
   ```

   The refresh token comes in a JSON body, not the `Authorization`
   header, so it never travels the same road as access tokens. The user
   is re-checked against the database, which is the one moment a
   long-lived login gets to notice that the account was deleted or
   deactivated. `carol` gets `401` here rather than `403`: from the
   client's point of view, the session is simply over.

5. **Rotation.** `/refresh` returns a **new refresh token** as well, and
   the client throws away the old one. An active user's refresh token
   keeps moving forward and never hits its 7-day limit; a user who
   disappears for a week has to log in again. The client's logic is:
   call the API with the access token; on `401`, call `/refresh` once,
   save both new tokens, retry; if `/refresh` also fails, send the user
   to the login screen.

6. **Where the client should keep them.** In a browser:
   - **Memory** (a JS variable) for the access token is safest, but it's
     lost on page reload, which is what the refresh token is for.
   - **`localStorage`** is easy and survives reloads, but any script on
     the page can read it, so one cross-site scripting (XSS) bug leaks
     the tokens.
   - An **`httpOnly` cookie** is the stronger option for the refresh
     token: JavaScript can't read it at all, and the browser sends it
     automatically. Add `Secure` (HTTPS only), `SameSite=Strict` or
     `Lax`, and a `Path` of `/refresh` so it goes nowhere else. Cookies
     bring their own risk (cross-site request forgery), which
     `SameSite` mostly handles.

   Mobile apps use the platform's secure storage (Keychain, Keystore).

7. **The catch: a JWT can't be taken back.** The server stores nothing
   about the tokens it issued; it only checks signatures. So "log out"
   or "rotate" can't cancel a token that's already out there. That's why
   using the same old refresh token twice still works in this lesson.
   The usual fixes all add server-side state:
   - **Denylist**: store the `jti` of every used or logged-out refresh
     token (Redis, with a TTL equal to its remaining lifetime) and
     reject it in `/refresh`. Reuse of a rotated token is then also a
     strong sign of theft, and you can end that user's sessions.
   - **Token version**: an integer column on the user, copied into each
     token. "Log out everywhere" increments it, and tokens carrying the
     old number stop working.
   - **Store refresh tokens in a table** and delete the row on logout.

   This lesson skips them so `sec_users` stays identical to 12/b, 12/c
   and 12/i (`create_all` can't add a column to an existing table). Short
   access-token lifetimes are what make this acceptable: the worst case
   for a leaked access token is 15 minutes.
