# 12/a — Password hashing

Storing passwords **safely**, before any tokens come into it. `POST
/register` hashes the password with Argon2 and stores only the hash.
`POST /login` checks a password against that hash. `GET /hash-demo`
hashes the same password twice so you can see that the two results are
different, yet both still verify. See [STEPS.md](STEPS.md) for a
line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `security.py`
(hashing). Table: `sec_a_users`, seeded with `alice` / `alice-password`,
`bob` / `bob-password` and `admin` / `admin-password`.

```bash
cd example/12/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `POST /register` | Create a user; `201`, `409` if the username is taken, `422` if the username isn't 3–30 chars or the password is under 8 |
| `POST /login` | Check username + password (JSON); `200` or `401 Incorrect username or password` |
| `GET /users` | Every user: `id` and `username` only, never the hash |
| `GET /hash-demo?password=secret` | Hash one password twice; two different hashes that both verify |

```bash
curl -X POST http://127.0.0.1:8000/register -H "Content-Type: application/json" -d "{\"username\": \"carol\", \"password\": \"carol-password\"}"

curl -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" -d "{\"username\": \"carol\", \"password\": \"carol-password\"}"

curl -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" -d "{\"username\": \"carol\", \"password\": \"wrong\"}"

curl http://127.0.0.1:8000/users

curl "http://127.0.0.1:8000/hash-demo?password=secret"
```

`/hash-demo` returns something like this (your hashes will differ, and
differ again on every call):

```json
{
  "password": "secret",
  "hash_1": "$argon2id$v=19$m=65536,t=3,p=4$f8NANaVFVHaDUzE0nOU1Mw$ysDJdNLURaZLI1G1Lv6s2hkLfuf8OqAT/X8uQq9Py8o",
  "hash_2": "$argon2id$v=19$m=65536,t=3,p=4$Y9fK0Jqwc/1b8BjVMXLKiA$2wbbXCA28hRZ8Sk0df/S9eLJnZwY/3J+lhkNmykjSM4",
  "hashes_equal": false,
  "verify_hash_1": true,
  "verify_hash_2": true,
  "verify_wrong_password": false
}
```

**Try this too:** log in as `ghost` (no such user), then as `alice` with
the wrong password. Both get the exact same `401` body. That's on
purpose; [STEPS.md](STEPS.md) step 6 explains why.

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/register`, Body →
raw → JSON:

```json
{"username": "carol", "password": "carol-password"}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
