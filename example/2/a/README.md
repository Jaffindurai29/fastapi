# 2/a — Basic path parameter

See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

```bash
cd example/2/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items/{item_id}` | `item_id: int` — non-integer values (e.g. `/items/foo`) return `422` |

`{item_id}` is a placeholder — replace it with a real number, don't paste
the braces literally:

```bash
curl http://127.0.0.1:8000/items/5
curl http://127.0.0.1:8000/items/foo   # 422, "foo" isn't an int
```

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/items/5` — no
Headers or Body needed.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
