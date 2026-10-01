# 7/a — MySQL backend, full CRUD + CORS

All five verbs from [topic 6](../../6) combined into one running app,
plus `CORSMiddleware` so the [React frontend](../react) can call it.
Same [setup](../../6/a/README.md#setup) as topic 6 — install
dependencies from the repo's `requirements.txt`, create the database,
set your connection env vars (or copy `.env.example` to `.env`, or
point `DATABASE_URL` at SQLite for a quick local try).

## Files

Same [layered structure](../../6/a/README.md#files) as topic 6 —
`database.py`/`models.py`/`schemas.py`/`crud.py`/`main.py` — except
`schemas.py` has both `ItemRequest` and `ItemPatch` (this app needs
both), `crud.py` has all six functions (one per verb, plus
`seed_items`), and `main.py` also registers `CORSMiddleware`. This
app's table is its own `crud_react_items`, separate from topic 6's
shared `items` table, so running this folder never touches topic 6's
data or vice versa.

```bash
cd example/7/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Every row (seeded with two on first run) |
| `GET /items/{item_id}` | One row by its database ID; `404` if missing |
| `POST /items` | Insert a new row; `201 Created` |
| `PUT /items/{item_id}` | Replace a row's value entirely; `404` if missing |
| `PATCH /items/{item_id}` | Partially update a row (field optional); `404` if missing |
| `DELETE /items/{item_id}` | Remove a row; `204 No Content`; `404` if missing |

```bash
curl http://127.0.0.1:8000/items
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"value\": \"third\"}"
curl -X PUT http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d "{\"value\": \"replaced\"}"
curl -X PATCH http://127.0.0.1:8000/items/2 -H "Content-Type: application/json" -d "{\"value\": \"patched\"}"
curl -i -X DELETE http://127.0.0.1:8000/items/3
```

**Postman:** same five requests as [topic 6](../../6) — Method +
`http://127.0.0.1:8000/items` (with `/{id}` where needed), Body → raw →
JSON where a body is needed.

## Thunder Client (VS Code)

Install once: VS Code → Extensions (`Ctrl+Shift+X`) → search
**Thunder Client** → Install. A ⚡ icon appears in the Activity Bar.
Then ⚡ → **New Request** for each of these, POST first:

| # | Method | URL | Body tab | Expected |
|---|---|---|---|---|
| 1 | `POST` | `http://127.0.0.1:8000/items` | **JSON**: `{"value": "third"}` | `201 Created`, `{"id": 3, "value": "third"}` |
| 2 | `GET` | `http://127.0.0.1:8000/items` | none | `200 OK`, every row |
| 3 | `GET` | `http://127.0.0.1:8000/items/3` | none | `200 OK`, that row (`404` for an unknown ID) |
| 4 | `PUT` | `http://127.0.0.1:8000/items/3` | **JSON**: `{"value": "replaced"}` | `200 OK`, updated row |
| 5 | `PATCH` | `http://127.0.0.1:8000/items/3` | **JSON**: `{"value": "patched"}` | `200 OK`, updated row |
| 6 | `DELETE` | `http://127.0.0.1:8000/items/3` | none | `204 No Content` |

Choose **JSON** in the Body tab, not Text or Form. A body that isn't a
JSON object, e.g. `` `value` = `first` ``, gets
`422 — "Input should be a valid dictionary or object"`.

Tip: save the requests into a Thunder Client **Collection** (e.g.
`mysql-react`) to re-run them with one click.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
