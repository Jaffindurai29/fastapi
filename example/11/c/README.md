# 11/c — Many-to-many

Tags. An item can have many tags, and a tag can be on many items, so
neither table can hold the link. A third table, `rel_item_tags`, stores
one row per (item, tag) pair. SQLAlchemy reads and writes it for you
through `relationship(..., secondary=...)`. See [STEPS.md](STEPS.md)
for the walkthrough.

Same [setup](../../6/a/README.md#setup) as topic 6, and the `routers/`
layout from [10/a](../../10/a). Tables: `rel_categories` and `rel_items`
(shared with 11/a and 11/b; their columns are unchanged here), plus new
`rel_tags` and `rel_item_tags`. Seeded with two tags: `sale` and `new`
on the Laptop, `new` on the FastAPI Guide.

```bash
cd example/11/c
uvicorn main:app --reload
```

| Route | Status | Description |
|---|---|---|
| `GET /tags` | `200` | Every tag |
| `POST /tags` | `201`, `409` | New tag; `409` if the name is taken |
| `GET /tags/{tag_id}/items` | `200`, `404` | Every item with that tag |
| `GET /items` | `200` | Every item with its `tags` |
| `GET /items/{item_id}` | `200`, `404` | One item with its `tags` |
| `POST /items` | `201`, `404`, `422` | New item; optional `tag_ids`; `404` if the category or any tag doesn't exist |
| `PUT /items/{item_id}/tags/{tag_id}` | `200`, `404` | Attach a tag. Already attached? Still `200`, nothing changes |
| `DELETE /items/{item_id}/tags/{tag_id}` | `204`, `404` | Detach a tag; `404` if it wasn't attached |

```bash
curl -X POST http://127.0.0.1:8000/tags -H "Content-Type: application/json" -d "{\"name\": \"gift\"}"

curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Keyboard\", \"price\": 49, \"category_id\": 1, \"tag_ids\": [1, 3]}"

curl -X PUT http://127.0.0.1:8000/items/2/tags/3

curl -X DELETE http://127.0.0.1:8000/items/2/tags/3

curl http://127.0.0.1:8000/tags/2/items
```

The Keyboard comes back with both tags:

```json
{"id": 5, "name": "Keyboard", "price": 49.0, "category_id": 1, "tags": [{"id": 1, "name": "sale"}, {"id": 3, "name": "gift"}]}
```

`"tag_ids": [1, 98, 99]` answers
`404 {"detail": "Tag(s) not found: [98, 99]"}` and creates nothing.

**Postman:** Method `PUT`, URL `http://127.0.0.1:8000/items/2/tags/3`,
no Body needed. For `POST /items`, Body → raw → JSON:

```json
{"name": "Keyboard", "price": 49, "category_id": 1, "tag_ids": [1, 3]}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
