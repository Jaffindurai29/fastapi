# 8/b — HTTPException & status codes

Choosing the **right** error code instead of answering everything with
`404` (or crashing with `500`). Adds `PATCH` and `DELETE` to 8/a's app,
so there are real situations for each code. See [STEPS.md](STEPS.md)
for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6. Shares the
`validation_items` table with [8/a](../a).

```bash
cd example/8/b
uvicorn main:app --reload
```

| Route | Success | Errors |
|---|---|---|
| `GET /items` | `200` | — |
| `GET /items/{item_id}` | `200` | `404` missing |
| `POST /items` | `201` | `409` name already taken, `422` invalid body |
| `PATCH /items/{item_id}` | `200` | `400` empty body or `null` value, `404` missing, `409` new name taken, `422` invalid |
| `DELETE /items/{item_id}` | `204` | `404` missing, `409` still in stock |

```bash
curl -i -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Laptop\", \"price\": 1}"

curl -i -X PATCH http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d "{}"

curl -i -X DELETE http://127.0.0.1:8000/items/1

curl -i -X PATCH http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d "{\"quantity\": 0}"

curl -i -X DELETE http://127.0.0.1:8000/items/1
```

`-i` prints the status line, so you can see `409`, `400`, `409`, `200`,
then `204`.

## Which code when?

| Code | Meaning | Example here |
|---|---|---|
| `400 Bad Request` | The request is well-formed, but makes no sense | `PATCH` with `{}` |
| `404 Not Found` | The thing in the URL doesn't exist | `GET /items/999` |
| `409 Conflict` | Valid request, but clashes with what's stored | duplicate name; deleting while in stock |
| `422 Unprocessable Content` | Body/params broke a validation rule | `price: -1` (FastAPI sends this for you) |
| `500 Internal Server Error` | Your code crashed. Never send this on purpose | — |

**Postman:** Method `PATCH`, URL `http://127.0.0.1:8000/items/1`, Body →
raw → JSON:

```json
{"price": 899}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
