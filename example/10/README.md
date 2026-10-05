# 10 — Project structure

Up to topic 8, each app was one `main.py` with every route in it, plus
a few helper modules. That stops scaling once an API has more than one
resource. This topic splits the app the way real FastAPI projects are
laid out: routes grouped into **routers**, shared "things a route
needs" pulled out into **dependencies**, every setting in one typed
**config** class. It ends with the question every FastAPI beginner hits
next: `async def` or `def`?

| Sub-topic | What it covers |
|---|---|
| [10/a — APIRouter](a) | Move routes into a `routers/` package; `prefix`, `tags`, `include_router`; a `/health` check. |
| [10/b — Dependency injection](b) | `dependencies.py`: `get_db` explained, `get_item_or_404`, a `Pagination` class, an `X-API-Key` guard on write routes. |
| [10/c — Settings](c) | `pydantic-settings`: one typed, validated `Settings` class from env vars and `.env`; `SecretStr`; CORS and `/info` from settings. |
| [10/d — `async def` vs `def`](d) | No database. Timing 5 concurrent requests shows why a blocking call inside `async def` freezes the server. |

10/a–10/c use the same [setup](../6/a/README.md#setup) as topic 6
(database, `.env`, SQLite fallback) and the `name`/`price`/`quantity`
item from [topic 8](../8). 10/d needs no database. Each folder has its
own **README.md** and **STEPS.md**.

10/a–10/c share one table, `structured_items`. The model is identical in
all three; only the code around it changes.
