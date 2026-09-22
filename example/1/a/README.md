# 1/a — Hello, FastAPI!

The simplest possible app: one route, no parameters. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

```bash
cd example/1/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /` | Returns `{"message": "Hello, FastAPI!"}` |

```bash
curl http://127.0.0.1:8000/
```

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/` — no Headers or
Body needed.

Try it at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) too.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
