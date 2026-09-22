# 2/b — Fixed path before dynamic path

`/users/me` is declared *before* `/users/{user_id}` — if it were declared
after, `/users/{user_id}` would match `/users/me` first and treat `"me"`
as a `user_id`. See [STEPS.md](STEPS.md) for a line-by-line walkthrough.

```bash
cd example/2/b
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /users/me` | Returns `{"user_id": "the current user"}` |
| `GET /users/{user_id}` | Returns `{"user_id": <str>}` for any other value |

```bash
curl http://127.0.0.1:8000/users/me
curl http://127.0.0.1:8000/users/hero
```

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/users/me` (or
`.../users/hero`) — no Headers or Body needed.

Try any route at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
