# 4/c — PUT

Replacing the item at a given index entirely. See [STEPS.md](STEPS.md)
for a line-by-line walkthrough.

```bash
cd example/4/c
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `PUT /items/{item_index}` | Replaces the whole item at that index (query parameter); out-of-range returns `404` |

```bash
curl -X PUT "http://127.0.0.1:8000/items/0?value=replaced"

curl -i -X PUT "http://127.0.0.1:8000/items/99?value=x"   # 404
```

**Postman:** Method `PUT`, URL `http://127.0.0.1:8000/items/0`, Params →
`value` = `replaced`.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
