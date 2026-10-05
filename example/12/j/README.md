# 12/j — Everything together + security checklist

Every piece of topic 12 in one app: hashed passwords, JWT login, access
**and** refresh tokens (with rotation), role checks, ownership checks,
a rate-limited login, and the boring-but-important production settings
(secrets from the environment, strict CORS, no `/docs` in production,
security headers). It's a small "secure notes" API: each user owns
their notes, admins can see everyone's. This is also the backend for
[12/react](../react).

[STEPS.md](STEPS.md) walks through it as a **security checklist**: each
item, where it lives in the code, and why it matters.

Same [setup](../../6/a/README.md#setup) as topic 6 (database, `.env`,
SQLite fallback). New in `.env.example`: `SECRET_KEY`, `ENVIRONMENT`,
token lifetimes, `CORS_ORIGINS`, `LOGIN_RATE_LIMIT`. All of them have
development defaults, so it still runs with zero setup.

## Files

| File | Responsibility |
|---|---|
| `config.py` | `Settings` (pydantic-settings): every setting and secret, read from env / `.env`; refuses a weak `SECRET_KEY` in production |
| `database.py` | `engine`, `SessionLocal`, `Base`, `get_db()`, using the URL from `config.py` |
| `models.py` | `secure_users`, `secure_notes`, `secure_refresh_tokens` tables |
| `schemas.py` | request bodies and `*Out` response models (no `hashed_password` anywhere) |
| `crud.py` | database functions + demo seed data |
| `security.py` | password hashing (pwdlib/argon2), creating and decoding JWTs |
| `dependencies.py` | `get_current_user`, `require_role(...)` |
| `rate_limit.py` | the shared slowapi `Limiter` |
| `routers/auth.py` | `/token`, `/refresh`, `/register` |
| `routers/users.py` | `/users/me`, `/admin/users` |
| `routers/notes.py` | notes CRUD with ownership checks |
| `main.py` | creates the app: docs switch, CORS, security headers, rate-limit handler, routers |

## Run it

```bash
cd example/12/j
uvicorn main:app --reload
```

Seeded users (only when the table is empty):

| Username | Password | Role |
|---|---|---|
| `alice` | `alice-password` | user (owns notes 1 and 2) |
| `bob` | `bob-password` | user (owns note 3) |
| `admin` | `admin-password` | admin |

| Route | Auth | Description |
|---|---|---|
| `POST /token` | none | Form body `username` + `password`. Returns `access_token` + `refresh_token`. `401` "Incorrect username or password"; `429` after 5 tries a minute |
| `POST /refresh` | none | JSON `{"refresh_token": "..."}`. Returns a **new pair**; the old refresh token stops working. `401` if expired, reused, or not a refresh token |
| `POST /register` | none | JSON `{"username", "password"}`. `201` (always role `user`), `409` if taken, `422` if invalid |
| `GET /users/me` | user | Who am I (`id`, `username`, `role`, `is_active`) |
| `GET /admin/users` | admin | Every user. `403` for non-admins |
| `GET /notes` | user | Your notes (admins: everyone's) |
| `POST /notes` | user | JSON `{"title", "body"}`. `201`; owner is always you |
| `GET /notes/{note_id}` | user | `404` if missing, `403` if not yours (admins may) |
| `PUT /notes/{note_id}` | user | Replace title + body. Same `404` / `403` |
| `DELETE /notes/{note_id}` | user | `204`. Same `404` / `403` |

Every route marked "user" or "admin" answers `401` without a valid
access token.

## Try it with curl

Log in (note: a **form** body, not JSON, as OAuth2 requires):

```bash
curl -X POST http://127.0.0.1:8000/token -d "username=alice&password=alice-password"
```

Copy `access_token` from the response and use it below in place of
`TOKEN` (and `refresh_token` in place of `REFRESH`):

```bash
curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer TOKEN"

curl http://127.0.0.1:8000/notes -H "Authorization: Bearer TOKEN"

curl -X POST http://127.0.0.1:8000/notes -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d "{\"title\": \"Groceries\", \"body\": \"Bread\"}"

curl -X PUT http://127.0.0.1:8000/notes/1 -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d "{\"title\": \"Edited\", \"body\": \"New body\"}"

curl -X DELETE http://127.0.0.1:8000/notes/1 -H "Authorization: Bearer TOKEN"

curl -X POST http://127.0.0.1:8000/refresh -H "Content-Type: application/json" -d "{\"refresh_token\": \"REFRESH\"}"

curl -X POST http://127.0.0.1:8000/register -H "Content-Type: application/json" -d "{\"username\": \"carol\", \"password\": \"carol-password\"}"
```

Things worth trying as `alice`:

- `curl http://127.0.0.1:8000/notes/3 -H "Authorization: Bearer TOKEN"`
  → `403` "You don't own this note" (it's Bob's).
- `curl http://127.0.0.1:8000/admin/users -H "Authorization: Bearer TOKEN"`
  → `403` "Not enough permissions". Log in as `admin` and it works.
- Run the same `/refresh` call twice → the second one is `401`
  "Refresh token is no longer valid" (rotation).
- Send the **refresh** token as the Bearer token to `/users/me` → `401`.
- Log in with a wrong password 6 times in a minute → the 6th answer is
  `429 Too Many Requests`, even if the password is right.
- Add `-i` to any curl to see the security headers
  (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`).
- Paste an access token into [jwt.io](https://jwt.io): the payload is
  readable by anyone (`sub`, `exp`, `type`). That's why nothing secret
  goes in it.

## Production mode

```bash
export ENVIRONMENT=production
uvicorn main:app
```

...refuses to start: `SECRET_KEY must be set in production`. Generate a
real one and try again:

```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
uvicorn main:app
```

Now it starts, and `/docs`, `/redoc` and `/openapi.json` all return
`404`.

**Postman:** for `/token` use Body → `x-www-form-urlencoded` with keys
`username` and `password`. For everything else, Authorization tab →
Type `Bearer Token` → paste the `access_token`. Or click
**Authorize** in `/docs`, which logs in through `/token` for you.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
