# 3/a — POST, create an item

Accepting a JSON body and returning it back. See [STEPS.md](STEPS.md)
for a line-by-line walkthrough.

```bash
cd example/3/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `POST /items` | Body: `{"name": "...", "price": ...}` — both required. Returns the parsed item back. |

```bash
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Laptop\", \"price\": 999.99}"
```

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/items`, Body →
raw → JSON:

```json
{"name": "Laptop", "price": 999.99}
```

Expected response: `{"name": "Laptop", "price": 999.99}`

Leave out `price` and try again — you'll get a `422` telling you exactly
which field is missing, without writing any validation code yourself.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
