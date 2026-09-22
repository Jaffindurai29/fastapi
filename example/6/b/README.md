# 6/b — POST (MySQL)

Adding a new row. Same [setup](../a/README.md#setup) and
[file layout](../a/README.md#files) as 6/a — this folder also has its
own `.env.example` (`cp .env.example .env` if you want one here too).
See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

```bash
cd example/6/b
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `POST /items` | Inserts a new row; returns `201 Created` with its real database ID |

```bash
curl -i -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"value\": \"third\"}"
```

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/items`, Body →
raw → JSON:

```json
{"value": "third"}
```

Expected response: `201 Created`, `{"id": 3, "value": "third"}`.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
