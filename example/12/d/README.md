# 12/d — Refresh tokens

Short-lived access, long-lived login. `POST /token` now returns **two**
tokens: an access token (15 minutes) for calling the API, and a refresh
token (7 days) whose only job is `POST /refresh`, which swaps it for a
brand-new pair without asking for the password. Each kind is rejected
where the other belongs. See [STEPS.md](STEPS.md) for a line-by-line
walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `config.py`,
`security.py` and `dependencies.py` from [12/c](../c).
`REFRESH_TOKEN_EXPIRE_DAYS` is new in `.env.example`. Table:
`sec_users`, shared with 12/b, 12/c and 12/i. Seeded users: `alice`,
`bob`, `admin` (password `<name>-password`), and `carol` /
`carol-password`, who is deactivated.

```bash
cd example/12/d
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `POST /token` | Form login → `access_token` + `refresh_token`; `401` if wrong |
| `POST /refresh` | JSON `{"refresh_token": "..."}` → a new pair; `401` if it's expired, invalid, or actually an access token |
| `GET /users/me` | Needs an **access** token; a refresh token gets `401` |

```bash
curl -X POST http://127.0.0.1:8000/token -d "username=alice&password=alice-password"

curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer <paste access_token>"

curl -X POST http://127.0.0.1:8000/refresh -H "Content-Type: application/json" -d "{\"refresh_token\": \"<paste refresh_token>\"}"
```

Login and `/refresh` both answer:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Mixing them up fails:

```bash
curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer <paste refresh_token>"

curl -X POST http://127.0.0.1:8000/refresh -H "Content-Type: application/json" -d "{\"refresh_token\": \"<paste access_token>\"}"
```

| What you send | Status | `detail` |
|---|---|---|
| Refresh token to `/users/me` | `401` | `Could not validate credentials` |
| Access token (or garbage) to `/refresh` | `401` | `Invalid refresh token` |
| Expired refresh token to `/refresh` | `401` | `Refresh token has expired` |
| `carol`'s refresh token to `/refresh` | `401` | `Invalid refresh token` |

**Try this too:** call `/refresh` twice with the **same, old** refresh
token. Both work. Rotation hands out a new refresh token each time, but
nothing marks the old one as used. [STEPS.md](STEPS.md) step 7 explains
why, and what real apps do about it.

**Postman:** `POST http://127.0.0.1:8000/refresh`, Body → raw → JSON:

```json
{"refresh_token": "<paste refresh_token>"}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
