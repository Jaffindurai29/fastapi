# 10/b — Dependency injection with `Depends`

Same folder layout and API as [10/a](../a), plus a new
`dependencies.py` that holds every reusable "thing a route needs before
it can run":

- `get_db` — the database session (moved here from `database.py`)
- `get_item_or_404` — loads the row from `{item_id}` or answers `404`,
  so GET, PATCH and DELETE no longer repeat that code
- `Pagination` — a class that reads and validates `?skip=&limit=`
- `require_api_key` — a guard: `POST`, `PATCH` and `DELETE` now need an
  `X-API-Key` header

See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) as topic 6, plus one new
optional variable in `.env.example`: `API_KEY` (default `dev-api-key`).

## Files

```
10/b/
├── main.py            # creates the app, include_router(...)
├── database.py        # engine, SessionLocal, Base
├── dependencies.py    # get_db, get_item_or_404, Pagination, require_api_key
├── models.py          # ItemModel -> table structured_items
├── schemas.py         # ItemCreate / ItemPatch / ItemOut
├── crud.py            # plain database functions, no HTTP
└── routers/
    ├── __init__.py
    ├── items.py       # /items — uses the dependencies above
    └── health.py      # GET /health
```

## Run it

```bash
cd example/10/b
uvicorn main:app --reload
```

| Route | Key? | Description |
|---|---|---|
| `GET /items?skip=0&limit=10` | no | A page of rows. `limit` 1–100 (default 10), `skip` 0 or more; `422` otherwise |
| `GET /items/{item_id}` | no | One row; `404` if missing |
| `POST /items` | yes | Insert; `201`, `401` without a valid key, `409` if the name is taken, `422` |
| `PATCH /items/{item_id}` | yes | Change only the fields sent; `401`, `400` if empty or `null`, `404`, `409` |
| `DELETE /items/{item_id}` | yes | Remove; `204`, `401`, or `404` |
| `GET /health` | no | Runs `SELECT 1`; `{"status": "ok", "database": "ok"}`, or `503` |

```bash
curl "http://127.0.0.1:8000/items?skip=1&limit=1"

curl http://127.0.0.1:8000/items/1

curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Desk\", \"price\": 120}"

curl -X POST http://127.0.0.1:8000/items -H "X-API-Key: dev-api-key" -H "Content-Type: application/json" -d "{\"name\": \"Desk\", \"price\": 120, \"quantity\": 2}"

curl -X PATCH http://127.0.0.1:8000/items/1 -H "X-API-Key: dev-api-key" -H "Content-Type: application/json" -d "{\"price\": 899}"

curl -X DELETE http://127.0.0.1:8000/items/2 -H "X-API-Key: dev-api-key"
```

The first `POST` (no key) comes back
`401 {"detail": "Missing or invalid API key"}`; the second one works.
Quote the URL with `?` and `&` in it, or your shell will cut it at the
`&`.

In [/docs](http://127.0.0.1:8000/docs), the three write routes show an
`x-api-key` header field; the read routes don't. `GET /items` shows
`skip` and `limit` with their limits, read straight from `Pagination`.

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/items`, Headers
tab → key `X-API-Key`, value `dev-api-key`, Body → raw → JSON:

```json
{"name": "Desk", "price": 120, "quantity": 2}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
