# Examples

Each numbered folder is one topic, and each lettered subfolder inside it
is one runnable, standalone snippet — its own `main.py`, run on its
own. The topic-level `README.md` is just an index; each lettered
subfolder has its own **README.md** (what it does, how to run it,
`curl`/Postman) and **STEPS.md** (a line-by-line walkthrough of the
code itself).

| Topic | Covers |
|---|---|
| [1 — GET](1) | Your first FastAPI app and route. |
| [2 — Path Parameters](2) | Reading dynamic values from the URL path. |
| [3 — POST](3) | Accepting a JSON body. |
| [4 — Array + CRUD](4) | All five verbs (GET/POST/PUT/PATCH/DELETE) over an in-memory array. |
| [5 — React + Array + CRUD](5) | Connecting a React frontend to topic 4's array backend, with CORS. |
| [6 — MySQL + CRUD](6) | The same five verbs, backed by a real MySQL table via SQLAlchemy. |
| [7 — React + MySQL + CRUD](7) | Connecting a React frontend to topic 6's MySQL backend, with CORS. |
| [8 — Validation & errors](8) | `Field` rules, the right status codes, one consistent error shape, `response_model`. |
| [9 — Query params, pagination & filtering](9) | `skip`/`limit`, search/filter/sort, `Query(...)` validation, a paged response envelope. |
| [10 — Project structure](10) | `APIRouter`, `Depends`, settings with `pydantic-settings`, async vs sync. |
| [11 — Relationships, transactions & soft delete](11) | One-to-many, nested responses, many-to-many, all-or-nothing transactions, soft delete. |
| [12 — Security](12) | Password hashing, JWT, protected routes, refresh tokens, roles, ownership, encryption, ID hashing, rate limiting, and a React login UI. |
| [13 — Database migrations](13) | Alembic instead of `create_all`. |

See the root [README.md](../README.md) for environment setup and how to
run any single sub-example (`cd example/<topic>/<letter>` then
`uvicorn main:app --reload`).
