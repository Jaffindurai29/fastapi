# 10/c — Settings with pydantic-settings

Same API as [10/b](../b), but every setting the app reads (database
connection, API key, app name, debug flag, CORS origins) now lives in
**one typed `Settings` class** in `config.py`, instead of `os.getenv`
calls scattered across `database.py` and `dependencies.py`. Settings are
read from environment variables and `.env`, converted to the right
types, and validated **once, at startup**. See [STEPS.md](STEPS.md) for
a line-by-line walkthrough.

New in the API: `GET /info`, the `/docs` page title comes from
`APP_NAME`, and CORS is on (origins from `CORS_ORIGINS`), so the
[topic 7 React app](../../7/react) style of frontend can call it.

Same [setup](../../6/a/README.md#setup) as topic 6. `.env.example` lists
every setting; all of them have defaults, so `.env` is still optional.

## Files

```
10/c/
├── main.py            # app (title/debug from settings), CORS, routers, GET /info
├── config.py          # class Settings(BaseSettings) + get_settings()
├── database.py        # engine built from get_settings()
├── dependencies.py    # get_db, get_item_or_404, Pagination, require_api_key
├── models.py          # ItemModel -> table structured_items
├── schemas.py         # ItemCreate / ItemPatch / ItemOut
├── crud.py
└── routers/
    ├── __init__.py
    ├── items.py
    └── health.py
```

## Run it

```bash
cd example/10/c
uvicorn main:app --reload
```

Try changing a setting without touching code:

```bash
APP_NAME="Shop API" DEBUG=true uvicorn main:app --reload
```

```powershell
# Windows (PowerShell)
$env:APP_NAME="Shop API"; $env:DEBUG="true"; uvicorn main:app --reload
```

| Route | Key? | Description |
|---|---|---|
| `GET /info` | no | `{"app_name": ..., "debug": ...}` — never secrets |
| `GET /items?skip=0&limit=10` | no | A page of rows; `422` if `skip`/`limit` are out of range |
| `GET /items/{item_id}` | no | One row; `404` if missing |
| `POST /items` | yes | Insert; `201`, `401`, `409`, `422` |
| `PATCH /items/{item_id}` | yes | Change only the fields sent; `401`, `400`, `404`, `409` |
| `DELETE /items/{item_id}` | yes | Remove; `204`, `401`, `404` |
| `GET /health` | no | Runs `SELECT 1`; `200` or `503` |

```bash
curl http://127.0.0.1:8000/info

curl "http://127.0.0.1:8000/items?limit=2"

curl -X POST http://127.0.0.1:8000/items -H "X-API-Key: dev-api-key" -H "Content-Type: application/json" -d "{\"name\": \"Desk\", \"price\": 120, \"quantity\": 2}"

curl -X DELETE http://127.0.0.1:8000/items/2 -H "X-API-Key: dev-api-key"
```

With the defaults, `/info` answers:

```json
{"app_name": "Structured Items API", "debug": false}
```

Set `API_KEY=something-else` and restart: the old `dev-api-key` now
gets `401`. Set `MYSQL_PORT=abc` and restart: the app refuses to start,
with a validation error naming `mysql_port`.

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/info`, no Headers
or Body. Write routes need the `X-API-Key` header, as in
[10/b](../b/README.md).

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
