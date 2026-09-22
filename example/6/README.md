# 6 — MySQL + CRUD

The same five verbs as [topic 4](../4), now backed by a real MySQL
table via SQLAlchemy instead of an in-memory array. See
[6/a's Setup section](a/README.md#setup) before running any of these —
it applies to all five.

| Sub-topic | Verb | What it covers |
|---|---|---|
| [6/a — GET](a) | `GET` | List every row, or reach one by its database ID. |
| [6/b — POST](b) | `POST` | Insert a new row. |
| [6/c — PUT](c) | `PUT` | Replace a row's value entirely, by ID. |
| [6/d — PATCH](d) | `PATCH` | Partially update a row — the field is optional. |
| [6/e — DELETE](e) | `DELETE` | Remove a row by ID. |

Each folder above has its own **README.md** (how to run it, routes,
`curl`/Postman), **STEPS.md** (line-by-line code walkthrough), and is
split into `database.py`/`models.py`/`schemas.py`/`crud.py`/`main.py`
instead of one file — see [6/a's Files section](a/README.md#files) for
what each one does.

All five folders point at the same `items` table (not five separate
tables), so they share state if run against the same database — if
you've already run another lesson against the same database, run
`GET /items` first to see which ids currently exist before trying a
`curl`/Postman example that references a specific id.

Want to call this from a browser? See [7 — React + MySQL + CRUD](../7), which
adds CORS and a real frontend on top of this same shape.
