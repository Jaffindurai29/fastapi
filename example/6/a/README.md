# 6/a — GET (MySQL)

Reading from a real MySQL table via SQLAlchemy — the whole table, and
one row by ID. Seeded with two rows so this works standalone. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough, and
[Setup](#setup) below before running it.

## Files

The code is split into layers instead of one file:

| File | Responsibility |
|---|---|
| `database.py` | env vars, `engine`, `SessionLocal`, `Base`, `get_db()` |
| `models.py` | `ItemModel` — the SQLAlchemy table |
| `crud.py` | plain functions that talk to the database, no HTTP |
| `main.py` | the `FastAPI()` app and the two routes |

## Setup

```bash
pip install -r ../../../requirements.txt
```

Create the database once, in your MySQL client:

```sql
CREATE DATABASE fastapi_learn;
```

Then either export connection details as environment variables (adjust
to match your MySQL install):

```bash
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your-password
export MYSQL_DB=fastapi_learn
```

...or copy `.env.example` to `.env` and edit it there instead — either
way works, since `database.py` loads `.env` automatically. Skipping
both is also fine: the defaults above (`root`, no password, on
`127.0.0.1`) are already baked in.

```bash
cp .env.example .env
```

No MySQL handy? Point it at a SQLite file instead — the same code works
unchanged:

```bash
export DATABASE_URL="sqlite:///./test.db"
```

## Run it

```bash
cd example/6/a
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Shows every row |
| `GET /items/{item_id}` | Reaches one row by its database ID; `404` if it doesn't exist |

```bash
curl http://127.0.0.1:8000/items
curl http://127.0.0.1:8000/items/1
```

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/items` (or
`.../items/1`) — no Headers or Body needed.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
