# 4/a — GET

Reading the array — the whole list, and one item by index. Seeded with
two items so this works standalone, no `POST` needed first. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

```bash
cd example/4/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Shows the whole array |
| `GET /items/{item_index}` | Reaches one specific item by its position; out-of-range returns `404` |

```bash
curl http://127.0.0.1:8000/items
curl http://127.0.0.1:8000/items/0
```

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/items` (or
`.../items/0`) — no Headers or Body needed.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
