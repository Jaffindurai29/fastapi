# 6/e — DELETE (MySQL)

Removing a row by ID. Same [setup](../a/README.md#setup) and
[file layout](../a/README.md#files) as 6/a — this folder also has its
own `.env.example` (`cp .env.example .env` if you want one here too).
See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

```bash
cd example/6/e
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `DELETE /items/{item_id}` | Removes that row; returns `204 No Content`; `404` if the ID doesn't exist |

```bash
curl -i -X DELETE http://127.0.0.1:8000/items/1

curl -i -X DELETE http://127.0.0.1:8000/items/99   # 404
```

**Postman:** Method `DELETE`, URL `http://127.0.0.1:8000/items/1` — no
Body needed.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
