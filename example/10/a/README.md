# 10/a — APIRouter

Moving routes out of `main.py`. Up to topic 8 every route lived in one
file, which is fine for five routes and painful for fifty. Here the
item routes go into `routers/items.py`, a health check goes into
`routers/health.py`, and `main.py` shrinks to "create the app, plug in
the routers". The API itself is the same full CRUD as
[8/b](../../8/b), returning `ItemOut` rows like [8/d](../../8/d). See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) as topic 6.

## Files

```
10/a/
├── main.py            # creates the app, include_router(...) — no routes
├── database.py        # engine, SessionLocal, Base, get_db()
├── models.py          # ItemModel -> table structured_items
├── schemas.py         # ItemCreate / ItemPatch / ItemOut
├── crud.py            # plain database functions, no HTTP
└── routers/
    ├── __init__.py    # makes routers/ a package (empty)
    ├── items.py       # router = APIRouter(prefix="/items", tags=["items"])
    └── health.py      # GET /health
```

## Run it

```bash
cd example/10/a
uvicorn main:app --reload
```

Run it from **inside** `10/a`. That's what makes `from routers import
items` and `import crud` work (see step 5 in [STEPS.md](STEPS.md)).

| Route | Description |
|---|---|
| `GET /items` | Every row |
| `GET /items/{item_id}` | One row; `404` if missing |
| `POST /items` | Insert; `201`, `409` if the name is taken, `422` if the body breaks a rule |
| `PATCH /items/{item_id}` | Change only the fields sent; `400` if empty or `null`, `404`, `409` |
| `DELETE /items/{item_id}` | Remove; `204`, or `404` |
| `GET /health` | Runs `SELECT 1`; `{"status": "ok", "database": "ok"}`, or `503` if the database is unreachable |

```bash
curl http://127.0.0.1:8000/items

curl http://127.0.0.1:8000/items/1

curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Desk\", \"price\": 120, \"quantity\": 2}"

curl -X PATCH http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d "{\"price\": 899}"

curl -X DELETE http://127.0.0.1:8000/items/2

curl http://127.0.0.1:8000/health
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs): the
routes now sit under two headings, **items** and **health**, one per
tag.

**Postman:** Method `PATCH`, URL `http://127.0.0.1:8000/items/1`, Body →
raw → JSON:

```json
{"price": 899}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
