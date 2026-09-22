# 4/e — DELETE

Removing the item at a given index. See [STEPS.md](STEPS.md) for a
line-by-line walkthrough.

```bash
cd example/4/e
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Returns the current list |
| `DELETE /items/{item_index}` | Removes that item; returns `204 No Content`; out-of-range returns `404` |

```bash
curl -i -X DELETE http://127.0.0.1:8000/items/0

curl -i -X DELETE http://127.0.0.1:8000/items/99   # 404
```

**Postman:** Method `DELETE`, URL `http://127.0.0.1:8000/items/0` — no
Body needed. A successful delete comes back with an empty response
body and status `204`.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
