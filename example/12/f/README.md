# 12/f — Authorization by ownership

Every note belongs to the user who created it. You can list, read, edit
and delete **your own** notes. Someone else's note is `403`; an admin can
touch any note. One dependency, `get_note_for_user`, does the
"does it exist, and is it yours?" check for every `/notes/{note_id}`
route. See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `config.py`,
`security.py` and `dependencies.py` from [12/b](../b) and [12/c](../c).
Tables: `sec_rbac_users` (shared with [12/e](../e)) and `sec_notes`.
Seeded users: `alice` / `alice-password` and `bob` / `bob-password`
(role `user`), `admin` / `admin-password` (role `admin`). Alice starts
with two notes, Bob with one.

```bash
cd example/12/f
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `POST /token` | Log in (form fields `username`, `password`); `401` if wrong |
| `GET /notes` | Your notes only; an admin gets everyone's |
| `POST /notes` | Body `{"title": "...", "body": "..."}`; `201`. The owner is always you |
| `GET /notes/{note_id}` | `404` if missing, `403` if not yours (and you're not admin) |
| `PUT /notes/{note_id}` | Replace title and body; same `404`/`403` rules |
| `DELETE /notes/{note_id}` | `204`; same `404`/`403` rules |

Every route except `/token` answers `401` without a valid token.

```bash
curl -X POST http://127.0.0.1:8000/token -d "username=alice&password=alice-password"

curl http://127.0.0.1:8000/notes -H "Authorization: Bearer <paste alice token>"

curl http://127.0.0.1:8000/notes/3 -H "Authorization: Bearer <paste alice token>"

curl -X POST http://127.0.0.1:8000/notes -H "Authorization: Bearer <paste alice token>" -H "Content-Type: application/json" -d "{\"title\": \"Ideas\", \"body\": \"learn FastAPI\"}"

curl -X PUT http://127.0.0.1:8000/notes/1 -H "Authorization: Bearer <paste alice token>" -H "Content-Type: application/json" -d "{\"title\": \"Shopping\", \"body\": \"milk, eggs, bread\"}"

curl -X DELETE http://127.0.0.1:8000/notes/3 -H "Authorization: Bearer <paste alice token>"
```

On a fresh database, note 3 is Bob's, so the third and last requests are
`403 {"detail": "Not enough permissions"}`. Log in as `admin` and the
same `DELETE` works.

**Postman:** `POST http://127.0.0.1:8000/token`, Body → x-www-form-urlencoded
with `username` and `password`. Copy `access_token`, then on the other
requests use Authorization → Bearer Token. Or click **Authorize** in
`/docs` and log in there.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
