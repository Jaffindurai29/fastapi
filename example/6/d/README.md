# 6/d — PATCH (MySQL)

Partially updating a row by ID — the field is optional. Same
[setup](../a/README.md#setup) and [file layout](../a/README.md#files)
as 6/a — this folder also has its own `.env.example` (`cp .env.example
.env` if you want one here too). See [STEPS.md](STEPS.md) for a
line-by-line walkthrough.

```bash
cd example/6/d
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `PATCH /items/{item_id}` | Updates `value` only if it's sent; `404` if the ID doesn't exist |

```bash
curl -X PATCH http://127.0.0.1:8000/items/2 -H "Content-Type: application/json" -d "{\"value\": \"patched\"}"

curl -X PATCH http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d "{}"
```

**Postman:** Method `PATCH`, URL `http://127.0.0.1:8000/items/2`, Body →
raw → JSON:

```json
{"value": "patched"}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
