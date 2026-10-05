# 9/c — `Query(...)` validation

The same filters as [9/b](../b), now with rules. `limit` is capped at
100, `skip` can't be negative, `search` needs 2–50 characters, prices
can't be negative, and `category` can be repeated to match several
categories at once. A second route takes the exact same filters as one
Pydantic model. See [STEPS.md](STEPS.md) for a line-by-line
walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6. Same
`catalog_items` table as 9/a.

```bash
cd example/9/c
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Filters as separate `Query(...)` parameters |
| `GET /items/search-model` | The same filters as one `FilterParams` model; unknown parameters are a `422` |
| `GET /items/{item_id}` | One row; `404` if missing |

| Query parameter | Rule | Default |
|---|---|---|
| `search` | 2–50 characters | not applied |
| `category` | Repeatable: `?category=books&category=toys` | not applied |
| `min_price` / `max_price` | `>= 0` | not applied |
| `sort_by` | `id`, `name`, `price`, `created_at` | `id` |
| `order` | `asc`, `desc` | `asc` |
| `skip` | `>= 0` | `0` |
| `limit` | `1`–`100` | `10` |

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs): every
parameter shows its description and its limits.

```bash
curl "http://127.0.0.1:8000/items?category=books&category=toys&limit=20"

curl "http://127.0.0.1:8000/items/search-model?category=kitchen&min_price=20&sort_by=price"

curl "http://127.0.0.1:8000/items?limit=500&search=a&skip=-1"

curl "http://127.0.0.1:8000/items/search-model?limt=5"
```

1. All 10 books and toys (`WHERE category IN ('books', 'toys')`).
2. Kitchen items from 20 up, cheapest first.
3. `422` with **three** errors, one per broken rule:

```json
{
  "detail": [
    {"type": "string_too_short", "loc": ["query", "search"], "msg": "String should have at least 2 characters", "...": "..."},
    {"type": "greater_than_equal", "loc": ["query", "skip"], "msg": "Input should be greater than or equal to 0", "...": "..."},
    {"type": "less_than_equal", "loc": ["query", "limit"], "msg": "Input should be less than or equal to 100", "...": "..."}
  ]
}
```

4. `422`, because `limt` is a typo and `FilterParams` forbids unknown
   parameters:

```json
{"detail": [{"type": "extra_forbidden", "loc": ["query", "limt"], "msg": "Extra inputs are not permitted", "input": "5"}]}
```

The same typo on `GET /items` is silently ignored: you get `200` with
the default 10 rows and no hint that your `limt` did nothing.

More `422` cases to try: `?limit=0`, `?limit=101`, `?min_price=-5`,
`?search=` followed by 51 characters, `?sort_by=secret`.

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/items`. In the
**Params** tab, add two rows both named `category` (values `books` and
`toys`) to send a repeated parameter.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
