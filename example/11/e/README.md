# 11/e — Soft delete

`DELETE` no longer deletes. It stamps the row with `deleted_at` and
every normal read pretends the row is gone. The row is still in the
table, so it can be listed on request, restored, or purged for real
later. See [STEPS.md](STEPS.md) for the walkthrough, including what this
costs.

Same [setup](../../6/a/README.md#setup) as topic 6, and the `routers/`
layout from [10/a](../../10/a). Own table: `soft_items`. Seeded with
Laptop, Mouse and Desk.

```bash
cd example/11/e
uvicorn main:app --reload
```

| Route | Status | Description |
|---|---|---|
| `GET /items` | `200` | Live items only |
| `GET /items?include_deleted=true` | `200` | Live **and** soft-deleted items |
| `GET /items/{item_id}` | `200`, `404` | One live item; `404` if missing **or** soft-deleted |
| `POST /items` | `201`, `422` | New item |
| `DELETE /items/{item_id}` | `204`, `404` | Soft delete: sets `deleted_at`; `404` if missing or already deleted |
| `POST /items/{item_id}/restore` | `200`, `404`, `409` | Undo a soft delete; `409` if it isn't deleted |
| `DELETE /items/{item_id}/permanent` | `204`, `404` | Real `DELETE`; works on live and soft-deleted rows |

```bash
curl -X DELETE http://127.0.0.1:8000/items/2

curl http://127.0.0.1:8000/items/2

curl "http://127.0.0.1:8000/items?include_deleted=true"

curl -X POST http://127.0.0.1:8000/items/2/restore

curl -X DELETE http://127.0.0.1:8000/items/2/permanent
```

After the first request, `GET /items/2` is a `404`, but the
`include_deleted` listing still has it:

```json
{"id": 2, "name": "Mouse", "price": 19.99, "deleted_at": "2026-10-05T10:28:35"}
```

Restore sets `deleted_at` back to `null`. Restoring a live item answers
`409 {"detail": "Item is not deleted"}`. After `/permanent` the row is
really gone: restore and every other route answer `404`.

The URL with `?` is in double quotes so the shell doesn't treat `?` as a
wildcard.

**Postman:** Method `POST`, URL
`http://127.0.0.1:8000/items/2/restore`, no Body needed. For the
listing, Method `GET`, URL `http://127.0.0.1:8000/items`, and under
**Params** add `include_deleted` = `true`.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
