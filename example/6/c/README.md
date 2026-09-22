# 6/c — PUT (MySQL)

Replacing a row entirely by ID. Same [setup](../a/README.md#setup) and
[file layout](../a/README.md#files) as 6/a — this folder also has its
own `.env.example` (`cp .env.example .env` if you want one here too).
See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

```bash
cd example/6/c
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `PUT /items/{item_id}` | Replaces the row's value; `404` if the ID doesn't exist |

```bash
curl -X PUT http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d "{\"value\": \"replaced\"}"

curl -i -X PUT http://127.0.0.1:8000/items/99 -H "Content-Type: application/json" -d "{\"value\": \"x\"}"   # 404
```

**Postman:** Method `PUT`, URL `http://127.0.0.1:8000/items/1`, Body →
raw → JSON:

```json
{"value": "replaced"}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
