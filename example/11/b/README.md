# 11/b — Nested responses

Same tables as [11/a](../a), different responses. An item now carries
its whole category, not just `category_id`, and a category carries the
list of its items. The routes load related rows up front with
`selectinload` / `joinedload`, so a list of items costs 2 queries
instead of one per item. See [STEPS.md](STEPS.md) for the walkthrough,
including the N+1 problem.

Same [setup](../../6/a/README.md#setup) as topic 6, and the `routers/`
layout from [10/a](../../10/a). Tables: `rel_categories` and
`rel_items`, shared with 11/a and 11/c (the models are identical).
Read-only: add data with 11/a.

```bash
cd example/11/b
uvicorn main:app --reload
```

| Route | Status | Response |
|---|---|---|
| `GET /items` | `200` | `list[ItemOut]`, each with a nested `category` |
| `GET /items/{item_id}` | `200`, `404` | `ItemOut` |
| `GET /categories` | `200` | `list[CategoryOut]` (no items) |
| `GET /categories/{category_id}` | `200`, `404` | `CategoryWithItems` |

```bash
curl http://127.0.0.1:8000/items/3

curl http://127.0.0.1:8000/categories/1
```

```json
{"id": 3, "name": "FastAPI Guide", "price": 39.0, "category": {"id": 2, "name": "Books"}}
```

```json
{"id": 1, "name": "Electronics", "items": [{"id": 1, "name": "Laptop", "price": 999.99}, {"id": 2, "name": "Mouse", "price": 19.99}]}
```

The items inside a category have **no** `category` field. That's on
purpose, see step 3 of [STEPS.md](STEPS.md).

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/categories/1`, no
Headers or Body needed.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
