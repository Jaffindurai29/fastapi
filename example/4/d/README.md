# 4/d — PATCH

Partially updating the item at a given index — `value` is optional and,
when sent, is merged onto the existing value instead of replacing it,
so PATCH visibly behaves differently from [4/c](../c/README.md)'s PUT.
See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

```bash
cd example/4/d
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Returns the current list |
| `PATCH /items/{item_index}` | Appends `value` onto the existing item if it's sent (query parameter); out-of-range returns `404` |

```bash
curl -X PATCH "http://127.0.0.1:8000/items/0?value=-patched"

curl -X PATCH http://127.0.0.1:8000/items/1
```

**Postman:** Method `PATCH`, URL `http://127.0.0.1:8000/items/0`, Params →
`value` = `-patched`.

Expected: `{"index": 0, "value": "first-patched"}` — try the request
with no `value` param too, and the item at that index comes back
unchanged.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
