# 9 — Query params, pagination & filtering

Every `GET /items` so far returned the **whole table**. That's fine for
two rows and a problem for two million. This topic teaches the list
endpoint to return one page at a time, to filter and sort on request,
to refuse nonsense parameters, and finally to tell the client how many
pages there are in total.

The table is a small product catalog, seeded with 25 rows across five
categories (`books`, `electronics`, `toys`, `kitchen`, `garden`), so
every filter and page has something visible to do.

| Sub-topic | What it covers |
|---|---|
| [9/a — skip/limit pagination](a) | `?skip=10&limit=5`; why you always `ORDER BY` before paging. |
| [9/b — Search, filter, sort](b) | Optional filters added one by one; `Literal` as a whitelist for `sort_by`. |
| [9/c — `Query(...)` validation](c) | `ge`/`le`/`min_length`, repeated `?category=`, and a Pydantic model for query params. |
| [9/d — Page envelope](d) | `?page=2&size=10` returning `items`, `total`, `page`, `size`, `pages`. |

Same [setup](../6/a/README.md#setup) as topic 6 (database, `.env`,
SQLite fallback) and the same layered
[file layout](../6/a/README.md#files), plus `schemas.py` and
`response_model` from [8/d](../8/d). Each folder has its own
**README.md** and **STEPS.md**.

All four share one table, `catalog_items` (identical model in every
folder), so you can switch between them without resetting anything.
