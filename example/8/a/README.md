# 8/a — Field validation

Rejecting bad input **before** your code runs. The `POST` body now has
rules: `name` 1–50 characters and not blank, `price` above 0,
`quantity` 0 or more. Break any rule and FastAPI answers
`422 Unprocessable Content` with a list of exactly what was wrong. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6.

```bash
cd example/8/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Every row |
| `GET /items/{item_id}` | One row; `404` if missing, `422` if the id isn't a number |
| `POST /items` | Insert a row; `201`, or `422` if the body breaks a rule |

```bash
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Desk\", \"price\": 120, \"quantity\": 2}"

curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"   \", \"price\": -5}"

curl http://127.0.0.1:8000/items/abc
```

The second request comes back `422` with **two** errors, one per broken
field:

```json
{
  "detail": [
    {"type": "value_error", "loc": ["body", "name"], "msg": "Value error, name must not be blank", "...": "..."},
    {"type": "greater_than", "loc": ["body", "price"], "msg": "Input should be greater than 0", "...": "..."}
  ]
}
```

**Try this too:** `POST` the same `name` twice. The second one fails with
a `500 Internal Server Error`. The database's `unique` rule caught it,
but nothing turned that into a proper response. [8/b](../b) fixes that.

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/items`, Body →
raw → JSON:

```json
{"name": "Desk", "price": 120, "quantity": 2}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
