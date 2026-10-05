# 9/d — Page envelope

`GET /items` now speaks in **page numbers** (`?page=2&size=10`) instead
of `skip`/`limit`, and wraps each page in an envelope that says how many
rows match in total and how many pages that makes. The filters and sort
from [9/b](../b) still work, and `total` counts only the rows they
match. See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6. Same
`catalog_items` table as 9/a.

```bash
cd example/9/d
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items?page=1&size=10` | One page inside an envelope; also takes `search`, `category`, `min_price`, `max_price`, `sort_by`, `order` |
| `GET /items/{item_id}` | One row; `404` if missing |

`page` must be `1` or more, `size` `1`–`100`. The other parameters
work as in 9/b, with 9/c's rules (`search` 2–50 characters, prices
`>= 0`).

```bash
curl "http://127.0.0.1:8000/items?page=2"

curl "http://127.0.0.1:8000/items?category=toys&size=2&page=3"

curl "http://127.0.0.1:8000/items?page=9"

curl "http://127.0.0.1:8000/items?page=0"
```

1. Rows 11–20, with `"total": 25, "page": 2, "size": 10, "pages": 3`.
2. The last toy. Only 5 rows are toys, so the numbers describe the
   filtered set, not the whole table:

```json
{
  "items": [{"id": 16, "name": "Plush Bear", "category": "toys", "price": 12.25, "created_at": "..."}],
  "total": 5,
  "page": 3,
  "size": 2,
  "pages": 3
}
```

3. Past the last page: `200` with `"items": []`, and `total`/`pages`
   still say where the data ends.
4. `422`, pages start at 1:

```json
{"detail": [{"type": "greater_than_equal", "loc": ["query", "page"], "msg": "Input should be greater than or equal to 1", "...": "..."}]}
```

A filter that matches nothing gives `"total": 0, "pages": 0` and an
empty `items` list.

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/items`, then
add `page`, `size` and any filters in the **Params** tab. Change `page`
and resend to step through the results.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
