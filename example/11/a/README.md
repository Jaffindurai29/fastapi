# 11/a — One-to-many

Two tables that point at each other. A **category** has many **items**;
every item belongs to exactly one category through a `category_id`
foreign key. Creating an item in a category that doesn't exist is a
`404`, and deleting a category that still has items is a `409`. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) as topic 6, and the `routers/`
layout from [10/a](../../10/a). Tables: `rel_categories` and
`rel_items` (shared with 11/b and 11/c). Seeded with 2 categories and
4 items.

```bash
cd example/11/a
uvicorn main:app --reload
```

| Route | Status | Description |
|---|---|---|
| `GET /categories` | `200` | Every category |
| `POST /categories` | `201`, `409` | New category; `409` if the name is taken |
| `GET /categories/{category_id}` | `200`, `404` | One category |
| `GET /categories/{category_id}/items` | `200`, `404` | The items in that category (`[]` if it's empty) |
| `DELETE /categories/{category_id}` | `204`, `404`, `409` | `409` while it still has items |
| `GET /items` | `200` | Every item, each with its `category_id` |
| `GET /items/{item_id}` | `200`, `404` | One item |
| `POST /items` | `201`, `404`, `422` | New item; `404` if `category_id` doesn't exist |

```bash
curl http://127.0.0.1:8000/categories/1/items

curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Keyboard\", \"price\": 49, \"category_id\": 1}"

curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Ghost\", \"price\": 5, \"category_id\": 999}"

curl -X DELETE http://127.0.0.1:8000/categories/1
```

The third request answers `404 {"detail": "Category 999 not found"}`.
The last one answers
`409 {"detail": "Category still has 3 item(s); move or delete them first"}`
(2 seeded items plus the Keyboard).

Responses are **flat**: an item shows `category_id: 1`, not the
category itself. [11/b](../b) nests it.

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/items`, Body →
raw → JSON:

```json
{"name": "Keyboard", "price": 49, "category_id": 1}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
