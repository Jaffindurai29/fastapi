# 12/e — Authorization by role

Logging in tells the API **who** you are. This lesson decides **what you
may do**. Every user has a `role` (`user` or `admin`), and a small
dependency factory, `require_role("admin")`, guards the admin routes.
Not logged in is `401`; logged in but not allowed is `403`. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `config.py`,
`security.py` and `dependencies.py` from [12/b](../b) and [12/c](../c).
Table: `sec_rbac_users` (shared with [12/f](../f)). Seeded users:
`alice` / `alice-password` and `bob` / `bob-password` (role `user`),
`admin` / `admin-password` (role `admin`).

```bash
cd example/12/e
uvicorn main:app --reload
```

| Route | Who | Description |
|---|---|---|
| `POST /token` | anyone | Log in (form fields `username`, `password`); `401` if wrong |
| `GET /users/me` | any logged-in user | Your own id, username and role |
| `GET /admin/users` | admin | Every user (never the password hash) |
| `PATCH /admin/users/{user_id}/role` | admin | Body `{"role": "user"}` or `{"role": "admin"}`; `404` if missing, `422` for any other role |
| `DELETE /admin/users/{user_id}` | admin | `204`; `400` if it's your own account, `404` if missing |

Every admin route answers `401` with no/bad token and `403
{"detail": "Not enough permissions"}` for a plain user.

```bash
curl -X POST http://127.0.0.1:8000/token -d "username=alice&password=alice-password"

curl http://127.0.0.1:8000/admin/users -H "Authorization: Bearer <paste alice token>"

curl -X POST http://127.0.0.1:8000/token -d "username=admin&password=admin-password"

curl http://127.0.0.1:8000/admin/users -H "Authorization: Bearer <paste admin token>"

curl -X PATCH http://127.0.0.1:8000/admin/users/1/role -H "Authorization: Bearer <paste admin token>" -H "Content-Type: application/json" -d "{\"role\": \"admin\"}"

curl -X DELETE http://127.0.0.1:8000/admin/users/2 -H "Authorization: Bearer <paste admin token>"
```

The second request is `403`. The fourth lists all three users.

**Try this too:** keep alice's token, promote her with the `PATCH`
above, then repeat the second request with the **same old token**. It's
now `200`. Demote her again and it's `403` again, without her logging in.
[STEPS.md](STEPS.md) step 5 explains why.

**Postman:** `POST http://127.0.0.1:8000/token`, Body → x-www-form-urlencoded
with `username` and `password`. Copy `access_token`, then on the other
requests use Authorization → Bearer Token. Or click **Authorize** in
`/docs` and log in there.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
