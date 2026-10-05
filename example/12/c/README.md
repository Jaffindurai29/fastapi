# 12/c — Protected routes

Using the token from [12/b](../b). A dependency,
`get_current_active_user`, reads the `Authorization: Bearer <token>`
header, verifies the token, and loads the user. Any route that asks for
it is locked: no token, a garbage token or an expired token gets `401`,
and a deactivated account gets `403`. `/public` stays open for
comparison. See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `config.py`,
`security.py` (both as in 12/b) and `dependencies.py` (the lock). Table:
`sec_users`, shared with 12/b, 12/d and 12/i. Seeded users: `alice`,
`bob`, `admin` (password `<name>-password`), and `carol` /
`carol-password`, who is deactivated.

```bash
cd example/12/c
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `POST /token` | Form login → access token (15 min); `401` if wrong |
| `GET /public` | No token needed |
| `GET /users/me` | The logged-in user; `401` without a valid token, `403` if deactivated |
| `GET /items` | Demo item list; same rules as `/users/me` |

Log in, then copy `access_token` from the response into the next
commands:

```bash
curl -X POST http://127.0.0.1:8000/token -d "username=alice&password=alice-password"

curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer <paste token>"

curl http://127.0.0.1:8000/items -H "Authorization: Bearer <paste token>"

curl http://127.0.0.1:8000/public
```

And the ways to fail:

```bash
curl http://127.0.0.1:8000/users/me

curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer garbage"

curl -X POST http://127.0.0.1:8000/token -d "username=carol&password=carol-password"
```

| What you send | Status | `detail` |
|---|---|---|
| No `Authorization` header | `401` | `Not authenticated` |
| A token that isn't valid (garbage, edited, wrong key) | `401` | `Could not validate credentials` |
| An expired token | `401` | `Token has expired` |
| A valid token for `carol` (deactivated) | `403` | `Inactive user` |

Every `401` also carries the header `WWW-Authenticate: Bearer`.

**Try this too:** to see an expired token without waiting 15 minutes,
put `ACCESS_TOKEN_EXPIRE_MINUTES=1` in `.env`, restart, log in, wait a
minute, and call `/users/me` again.

**/docs:** click **Authorize** (top right), enter `alice` /
`alice-password`, and every locked route (shown with a padlock) now
sends the token for you. Click **Logout** in the same dialog to try them
without it.

**Postman:** log in with Body → x-www-form-urlencoded (`username`,
`password`). Then on the protected request open the **Authorization**
tab → Type **Bearer Token** and paste the token.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
