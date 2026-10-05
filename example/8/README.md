# 8 — Validation & errors

Topic 6 trusted whatever the client sent and only ever answered `404`.
This topic makes the API strict about what comes **in** (validation),
precise about what goes **out** when something's wrong (status codes and
a consistent error shape), and careful about which fields leave the
server at all (`response_model`).

The item now has three fields instead of one, so there's something to
validate: `name` (unique), `price`, and `quantity`.

| Sub-topic | What it covers |
|---|---|
| [8/a — Field validation](a) | `Field(...)` rules and a `@field_validator`; what a `422` looks like. |
| [8/b — HTTPException & status codes](b) | Picking the right code: `400` vs `404` vs `409`. |
| [8/c — Custom exception handlers](c) | One consistent error shape for every error the API can return. |
| [8/d — `response_model` & status codes](d) | Return ORM rows directly; hide internal fields; `201`/`204`. |

Same [setup](../6/a/README.md#setup) as topic 6 (database, `.env`,
SQLite fallback) and the same layered
[file layout](../6/a/README.md#files). Each folder has its own
**README.md** and **STEPS.md**.

8/a–8/c share one table, `validation_items`. 8/d has its own,
`response_model_items`, because it adds two columns.
