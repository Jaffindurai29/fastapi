# 12/i — Rate limiting login

Slowing down password guessing. Argon2 ([12/a](../a)) makes each guess
expensive offline, but an attacker can still hammer `POST /token`
online. Here [slowapi](https://github.com/laurentS/slowapi) allows **5
login attempts per minute per IP address**; the 6th gets `429 Too Many
Requests` until the minute is up. `GET /users/me` is protected exactly
as in [12/c](../c). See [STEPS.md](STEPS.md) for a line-by-line
walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `config.py`,
`security.py` and `dependencies.py` from 12/c. Table: `sec_users`,
shared with 12/b, 12/c and 12/d. Seeded users: `alice`, `bob`, `admin`
(password `<name>-password`), and `carol` / `carol-password`, who is
deactivated.

```bash
cd example/12/i
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `POST /token` | Form login → access token; `401` if wrong, `429` after 5 attempts in a minute (right or wrong) |
| `GET /users/me` | The logged-in user; `401` without a valid token, `403` if deactivated. Not rate limited |

```bash
curl -i -X POST http://127.0.0.1:8000/token -d "username=alice&password=alice-password"

curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer <paste token>"
```

`-i` prints the response headers. A successful login shows your budget:

```
x-ratelimit-limit: 5
x-ratelimit-remaining: 4
x-ratelimit-reset: 1791196147.93
```

Now run this one **six times** quickly:

```bash
curl -i -X POST http://127.0.0.1:8000/token -d "username=alice&password=wrong"
```

Attempts 2–5 are `401 Incorrect username or password`. The 6th (and any
login from your IP, even with the right password, even as `bob`) is:

```
HTTP/1.1 429 Too Many Requests
x-ratelimit-limit: 5
x-ratelimit-remaining: 0
x-ratelimit-reset: 1791196147.93
retry-after: 60

{"error":"Rate limit exceeded: 5 per 1 minute"}
```

`retry-after` is in seconds; `x-ratelimit-reset` is the Unix time when
the window resets. Your token from the first login keeps working on
`/users/me` the whole time.

**Try this too:** restart the server (or save a file so `--reload`
restarts it) and you can log in again at once. The counters live in
memory; [STEPS.md](STEPS.md) step 6 says why that's not good enough in
production.

**Postman:** `POST http://127.0.0.1:8000/token`, Body →
x-www-form-urlencoded (`username`, `password`). Press Send six times and
check the **Headers** tab of the response.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
