# 8/d — `response_model` & status codes

So far every route built its response by hand
(`{"id": row.id, "name": row.name, ...}`). Here the routes return the
database row **directly**, and `response_model=ItemOut` decides which
fields leave the server. The table has an internal `supplier_cost`
column that the client can *send* but never *see*. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6. Own table:
`response_model_items`.

```bash
cd example/8/d
uvicorn main:app --reload
```

| Route | Status | Response |
|---|---|---|
| `GET /items` | `200` | `list[ItemOut]` |
| `GET /items/{item_id}` | `200`, `404` | `ItemOut` |
| `POST /items` | `201 Created` | `ItemOut` |
| `DELETE /items/{item_id}` | `204 No Content`, `404` | no body |

```bash
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Desk\", \"price\": 120, \"supplier_cost\": 80}"

curl http://127.0.0.1:8000/items/1
```

The response has `id`, `name`, `price`, `quantity` and `created_at`, but
no `supplier_cost`, even though it was just stored:

```json
{"id": 3, "name": "Desk", "price": 120.0, "quantity": 0, "created_at": "2026-10-05T10:18:17"}
```

Open [/docs](http://127.0.0.1:8000/docs) and you'll see each route's
exact response schema, plus the `404` response declared with
`responses=`.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
