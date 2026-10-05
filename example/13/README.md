# 13 — Database migrations (Alembic)

Every app so far called `Base.metadata.create_all()` at startup. That
works exactly once: it creates **missing** tables, but it never changes a
table that's already there. Add a column to a model and `create_all`
silently does nothing, so the code expects a column the database doesn't
have. This is why topic 8/d needed its own table name instead of
adding two columns to the old one.

Migrations fix that. Each schema change is a small Python file with an
`upgrade()` and a `downgrade()`, numbered in order, committed to git,
and applied with one command. The database remembers which ones it has
already run.

| Sub-topic | What it covers |
|---|---|
| [13/a — Alembic instead of `create_all`](a) | Two hand-written migrations, `upgrade`/`downgrade`/`history`, and `--autogenerate` for the next change. |

Same [setup](../6/a/README.md#setup) as topic 6 (database, `.env`,
SQLite fallback). The folder has its own **README.md** and **STEPS.md**.

13/a uses its own table, `migrated_items`, and its own version table,
`alembic_version_13a`. It's safe to run in the same `fastapi_learn`
database as every other topic: its Alembic setup is told to ignore every
table that isn't its own (see [13/a](a/README.md#important-the-database-is-shared)).
