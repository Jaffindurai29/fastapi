# 11 — Relationships, transactions & soft delete (MySQL)

Every app so far had one table. Real data lives in several tables that
point at each other: an item belongs to a category, an item has many
tags, an order has many lines. This topic links tables with foreign
keys and SQLAlchemy `relationship()`, returns nested JSON without
flooding the database with queries, makes multi-step writes
all-or-nothing with a transaction, and "deletes" rows without losing
them.

| Sub-topic | What it covers |
|---|---|
| [11/a — One-to-many](a) | `ForeignKey`, `relationship()`, `back_populates`; checking a foreign key in code (`404`); refusing to delete a parent that still has children (`409`). |
| [11/b — Nested responses](b) | `category` inside an item, `items` inside a category; the N+1 query problem; `selectinload` / `joinedload`; why `ItemSummary` exists. |
| [11/c — Many-to-many](c) | Tags through an association table (`secondary=`); attach/detach routes; idempotent `PUT`. |
| [11/d — Transactions](d) | Placing an order: one `commit` at the end, `rollback` on any error. An `/orders/unsafe` twin shows the half-written order you get otherwise. |
| [11/e — Soft delete](e) | A `deleted_at` column instead of `DELETE`; hide, restore, purge; what it costs. |

Same [setup](../6/a/README.md#setup) as topic 6 (database, `.env`,
SQLite fallback). The code layout is the one from
[topic 10](../10): `main.py` only builds the app, and each resource gets
its own module in `routers/`. Each folder has its own **README.md** and
**STEPS.md**.

11/a–11/c share two tables, `rel_categories` and `rel_items`. Their
columns are identical in all three; 11/c only adds a Python-side
relationship plus two new tables, `rel_tags` and `rel_item_tags`. 11/d
has its own `shop_products`, `shop_orders` and `shop_order_lines`. 11/e
has its own `soft_items`.
