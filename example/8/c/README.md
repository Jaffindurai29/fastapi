# 8/c — Custom exception handlers

Every error from this API, whatever caused it, now has **one shape**:

```json
{"error": {"code": "item_not_found", "message": "Item 99 not found"}}
```

Validation errors add a `fields` list. A frontend needs just one piece
of code to show any error. The routes and rules are the same as in
[8/b](../b), but the routes no longer contain any error handling. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) as topic 6. One new file:

| File | Responsibility |
|---|---|
| `exceptions.py` | `AppError` and its subclasses: business errors that each carry a status code and an error code |

```bash
cd example/8/c
uvicorn main:app --reload
```

| Route | Errors (all in the shape above) |
|---|---|
| `GET /items/{item_id}` | `item_not_found` (404) |
| `POST /items` | `duplicate_name` (409), `validation_error` (422) |
| `PATCH /items/{item_id}` | `empty_update` (400), `item_not_found`, `duplicate_name`, `validation_error` |
| `DELETE /items/{item_id}` | `item_not_found`, `item_in_stock` (409) |
| `GET /boom` | `internal_error` (500), from a deliberately broken route |
| any unknown URL | `http_404`; the wrong method gives `http_405` |

```bash
curl http://127.0.0.1:8000/items/99

curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"\", \"price\": -1}"

curl http://127.0.0.1:8000/nope

curl http://127.0.0.1:8000/boom
```

The second request returns:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request",
    "fields": [
      {"field": "body.name", "message": "String should have at least 1 character"},
      {"field": "body.price", "message": "Input should be greater than 0"}
    ]
  }
}
```

`/boom` answers `"Something went wrong"`. The real `ZeroDivisionError`
and its traceback go to the server's terminal, never to the client.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
