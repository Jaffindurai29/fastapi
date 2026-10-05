# 9/a — skip/limit pagination

Returning the list **one page at a time**. `GET /items` now reads two
query parameters, `skip` (how many rows to jump over) and `limit` (how
many to return), and defaults to the first 10 rows. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6. The table,
`catalog_items`, is seeded with 25 rows the first time you run it.

```bash
cd example/9/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items?skip=0&limit=10` | One page of rows, ordered by `id`. Both parameters are optional |
| `GET /items/{item_id}` | One row; `404` if missing |

```bash
curl http://127.0.0.1:8000/items

curl "http://127.0.0.1:8000/items?skip=10&limit=5"

curl "http://127.0.0.1:8000/items?skip=100"

curl "http://127.0.0.1:8000/items?limit=ten"
```

1. Rows 1–10 (the defaults).
2. Rows 11–15.
3. `[]`: past the end is an empty list, not an error.
4. `422`, `limit` must be an integer:

```json
{"detail": [{"type": "int_parsing", "loc": ["query", "limit"], "msg": "Input should be a valid integer, unable to parse string as an integer", "input": "ten"}]}
```

Put the URL in double quotes whenever it contains `&`, otherwise the
shell treats `&` as "run in the background" and cuts the URL short.

**Try this too:** `?limit=1000000`. It works, and returns every row.
Nothing stops a client from asking for the whole table again.
[9/c](../c) puts a ceiling on `limit`.

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/items`, then
use the **Params** tab to add `skip` and `limit`; Postman builds the
`?skip=...&limit=...` part of the URL for you.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
