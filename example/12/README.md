# 12 — Security

So far, anyone could call any route. This topic adds the questions
every real API has to answer: **who are you** (authentication), **what
may you do** (authorization), and **what must never leak** (passwords,
secrets, sensitive data, internal ids). Each letter teaches one piece
on its own. [12/j](j) puts them all together with a security
checklist, and [12/react](react) is a frontend that logs in and keeps
tokens fresh.

| Sub-topic | What it covers |
|---|---|
| [12/a — Password hashing](a) | Storing passwords as argon2 hashes with pwdlib, and checking them. |
| [12/b — Authentication with JWT](b) | `POST /token` with a username + password form, returning a signed access token. |
| [12/c — Protected routes](c) | A `get_current_user` dependency: no valid token, no access (`401`). |
| [12/d — Refresh tokens](d) | Short-lived access tokens plus a longer-lived refresh token to get new ones. |
| [12/e — Authorization by role](e) | Admin-only routes; `403` vs `401`. |
| [12/f — Authorization by ownership](f) | Users may only touch their own rows. |
| [12/g — Encrypt/decrypt fields](g) | Fernet: encrypt sensitive columns at rest, decrypt when reading. |
| [12/h — ID hashing](h) | sqids: short, non-sequential public ids instead of 1, 2, 3. |
| [12/i — Rate limiting login](i) | slowapi: `429 Too Many Requests` after too many login attempts. |
| [12/j — Everything together + security checklist](j) | One "secure notes" API with all of the above, plus production settings (secrets from env, CORS, no docs, security headers). |
| [12/react — React frontend](react) | Login UI, where to store tokens, axios interceptors that refresh and retry. |

Same [setup](../6/a/README.md#setup) as topic 6 (database, `.env`,
SQLite fallback) and the same layered
[file layout](../6/a/README.md#files), with a few new files:
`config.py`, `security.py`, `dependencies.py` and a `routers/` folder.
Each folder has its own **README.md** and **STEPS.md**.

Every letter that has users seeds them if its table is empty:

| Username | Password | Seeded in |
|---|---|---|
| `alice` | `alice-password` | every letter with users |
| `bob` | `bob-password` | every letter with users |
| `admin` | `admin-password` | every letter with users |
| `carol` | `carol-password` | 12/b, 12/c, 12/d, 12/i only, with `is_active=False` (log in or use her token to see `403` "Inactive user") |

Roles only exist from [12/e](e) onward (12/e, 12/f, 12/j). There,
`admin` has the role `admin` and everyone else has `user`. In 12/a–d
and 12/i, `admin` is just a username with no extra powers.

## Hashing vs encryption vs encoding/signing

Three different tools that are easy to mix up:

| | Reversible? | Needs a key? | Use it for | In this topic |
|---|---|---|---|---|
| **Hashing** | No, one-way. You can only check "does this input match?" | No (a salt is stored inside the hash) | Passwords. You never need to read them back, only verify them. | [12/a](a), pwdlib / argon2 |
| **Encryption** | Yes, two-way, with the key | Yes, and whoever has it can decrypt | Sensitive data you must read back later (phone numbers, API keys of your users, ...) | [12/g](g), Fernet |
| **Encoding + signing (JWT)** | Yes, by **anyone**. The payload is just base64. | The key only **signs**. It proves the token wasn't tampered with. | Saying who someone is (`sub`) in a way they can't forge | [12/b](b), PyJWT HS256 |

The practical rules that follow:

- Never encrypt passwords. Hash them.
- Never put secrets in a JWT. Anyone holding it can read it. Paste one
  into [jwt.io](https://jwt.io) to see for yourself.
- sqids ([12/h](h)) is **encoding**, not security: it hides the shape
  of an id, but the real protection is still the ownership check.

## How to run 12/j + 12/react

Like [topic 7](../7/README.md), the frontend needs the backend running
at the same time:

1. **One-time database setup** (identical to [topic 6](../6), skip if
   already done):

   ```bash
   pip install -r ../../requirements.txt
   ```

   ```sql
   CREATE DATABASE fastapi_learn;
   ```

   Export `MYSQL_*` variables or `cp example/12/j/.env.example
   example/12/j/.env` and edit it. Skipping both is also fine; the
   defaults are baked in. No MySQL handy?
   `export DATABASE_URL="sqlite:///./test.db"` instead.

   `SECRET_KEY` has a development default too. You only **must** set it
   when running with `ENVIRONMENT=production`, and the app refuses to
   start until you do.

2. **Terminal 1 — backend:**

   ```bash
   cd example/12/j
   uvicorn main:app --reload
   ```

3. **Terminal 2 — frontend:**

   ```bash
   cd example/12/react
   npm install
   npm run dev
   ```

4. Open the URL Vite prints (usually
   [http://localhost:5173](http://localhost:5173)) and log in as
   `alice` / `alice-password`.

Start the backend before the frontend: every button in the UI calls it
directly.

## Tables

Letters whose user model is identical share a table (`create_all`
never alters an existing table, so they must match exactly). When a
letter adds a column such as `role`, it gets its own table instead.
12/j uses `secure_users`, `secure_notes` and `secure_refresh_tokens`.
