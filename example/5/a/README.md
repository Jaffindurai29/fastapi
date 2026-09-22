# 5/a — Array backend, full CRUD + CORS

All five verbs from [topic 4](../../4) (GET, POST, PUT, PATCH, DELETE)
combined into one running app, plus `CORSMiddleware` so a browser page
on a different port (the [React frontend](../react)) is allowed to call
it. See [STEPS.md](STEPS.md) for what's different from topic 4.

```bash
cd example/5/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Shows the whole array (seeded with two items) |
| `GET /items/{item_index}` | Reaches one item by index; `404` if out of range |
| `POST /items` | Appends a new item; `201 Created` |
| `PUT /items/{item_index}` | Replaces an item entirely; `404` if out of range |
| `PATCH /items/{item_index}` | Partially updates an item (field optional); `404` if out of range |
| `DELETE /items/{item_index}` | Removes an item; `204 No Content`; `404` if out of range |

```bash
curl http://127.0.0.1:8000/items
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"value\": \"third\"}"
curl -X PUT http://127.0.0.1:8000/items/0 -H "Content-Type: application/json" -d "{\"value\": \"replaced\"}"
curl -X PATCH http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d "{\"value\": \"patched\"}"
curl -i -X DELETE http://127.0.0.1:8000/items/2
```

**Postman:** same five requests as [topic 4](../../4) — Method +
`http://127.0.0.1:8000/items` (with `/{index}` where needed), Body →
raw → JSON where a body is needed.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
