# 12/b — JWT login

Logging in now returns a **token**: a signed string the client sends on
later requests instead of the password. `POST /token` checks the
password (Argon2, as in [12/a](../a)) and returns a JWT that expires in
15 minutes. `GET /token/inspect` takes a token apart so you can see that
anyone can **read** it, but only the server can **make** a valid one.
See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `config.py`
(secret key, expiry) and `security.py` (hashing + tokens). `SECRET_KEY`
and `ACCESS_TOKEN_EXPIRE_MINUTES` are new in `.env.example`; the
defaults work with zero setup.

Table: `sec_users`, shared with 12/c, 12/d and 12/i. Seeded users:
`alice` / `alice-password`, `bob` / `bob-password`, `admin` /
`admin-password`, and `carol` / `carol-password` (deactivated, which
matters from [12/c](../c) on).

```bash
cd example/12/b
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `POST /token` | Form fields `username`, `password` → `{"access_token": "...", "token_type": "bearer"}`; `401` if wrong |
| `GET /token/inspect?token=...` | Header + payload (read **without** the key), plus whether the signature and expiry check out; `400` if it isn't a JWT |

Login is a **form**, not JSON (`-d` without a `Content-Type` header
sends a form):

```bash
curl -X POST http://127.0.0.1:8000/token -d "username=alice&password=alice-password"

curl -X POST http://127.0.0.1:8000/token -d "username=alice&password=wrong"

curl "http://127.0.0.1:8000/token/inspect?token=<paste token>"
```

A valid token inspects as:

```json
{
  "header": {"alg": "HS256", "typ": "JWT"},
  "payload": {"sub": "alice", "exp": 1791196775, "type": "access"},
  "valid": true,
  "verified_payload": {"sub": "alice", "exp": 1791196775, "type": "access"}
}
```

**Try this too:** paste your token into [jwt.io](https://jwt.io). It
shows `"sub": "alice"` without knowing the key. Edit the payload there
to `"sub": "admin"`, copy the new token, and inspect it here: the
payload says `admin`, but `"valid": false, "error": "Signature
verification failed"`. Wait 15 minutes and inspect the original token:
`"Signature has expired"`.

**Heads-up:** the default `SECRET_KEY` is a public, dev-only value. If
you set a key shorter than 32 bytes, PyJWT prints an
`InsecureKeyLengthWarning`. Generate a real one for anything beyond
your laptop.

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/token`, Body →
x-www-form-urlencoded → keys `username` = `alice`, `password` =
`alice-password`. JSON will get a `422`.

**/docs:** the `/token` route shows a form with `username` and
`password` fields. The "Authorize" button appears in [12/c](../c), once
there are routes that need a token.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
