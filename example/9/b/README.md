# 9/b — Search, filter, sort

The same paged `GET /items` as [9/a](../a), now with optional filters
(search by name, category, price range) and a choice of sort column and
direction. Send any combination, or none. See [STEPS.md](STEPS.md) for
a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6. Same
`catalog_items` table as 9/a.

```bash
cd example/9/b
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | One page of rows, filtered and sorted. All parameters optional (below) |
| `GET /items/{item_id}` | One row; `404` if missing |

| Query parameter | Effect | Default |
|---|---|---|
| `search` | Name contains this text, case-insensitive | not applied |
| `category` | Exact category (`books`, `electronics`, `toys`, `kitchen`, `garden`) | not applied |
| `min_price` / `max_price` | Price range, inclusive | not applied |
| `sort_by` | `id`, `name`, `price` or `created_at` | `id` |
| `order` | `asc` or `desc` | `asc` |
| `skip` / `limit` | Paging, as in 9/a | `0` / `10` |

```bash
curl "http://127.0.0.1:8000/items?search=chef"

curl "http://127.0.0.1:8000/items?category=electronics&max_price=100&sort_by=price"

curl "http://127.0.0.1:8000/items?sort_by=price&order=desc&limit=3"

curl "http://127.0.0.1:8000/items?sort_by=password"
```

1. `Chef's Knife`. `chef`, `CHEF` and `Chef` all match.
2. Electronics under 100, cheapest first: `USB-C Cable`, `Mouse`,
   `Mechanical Keyboard`.
3. The three most expensive items: `Laptop`, `Lawn Mower`,
   `27in Monitor`.
4. `422`, because `sort_by` only accepts the four listed columns:

```json
{"detail": [{"type": "literal_error", "loc": ["query", "sort_by"], "msg": "Input should be 'id', 'name', 'price' or 'created_at'", "input": "password", "...": "..."}]}
```

A filter that matches nothing (`?category=furniture`) is `200` with
`[]`, not an error.

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/items`, then
add the parameters you want in the **Params** tab. Untick a row to
leave that filter out without deleting it.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
