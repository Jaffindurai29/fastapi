# 4/b — POST

Adding a new item to the end of the array. Seeded with two items so
you can see the new one land after them. See [STEPS.md](STEPS.md) for a
line-by-line walkthrough.

```bash
cd example/4/b
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Returns the current list |
| `POST /items` | Appends one value (query parameter); returns the new item's index |

```bash
curl http://127.0.0.1:8000/items

curl -i -X POST "http://127.0.0.1:8000/items?value=third"
```

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/items`, Params →
`value` = `third`.

Expected response: `200 OK`, `{"index": 2, "value": "third"}`.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
