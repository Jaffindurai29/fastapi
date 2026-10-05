# 12/h — Public ids with sqids

URLs like `/items/1`, `/items/2`, `/items/3` tell the world how many rows
you have and invite people to try the next number. Here the database
still uses plain integer ids, but the API only ever shows a short,
non-sequential **public id** like `igPHZLIU`, made with
[sqids](https://sqids.org/python). `/items/1` is now a `404`. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

Same [setup](../../6/a/README.md#setup) and
[file layout](../../6/a/README.md#files) as topic 6, plus `config.py`
and `ids.py`. Table: `public_id_items`, seeded with three items. No
login in this lesson.

```bash
cd example/12/h
uvicorn main:app --reload
```

| Route | Description |
|---|---|
| `GET /items` | Every item, each with its public `id` |
| `GET /items/{public_id}` | One item; `404` if the id is invalid **or** unknown |
| `POST /items` | Body `{"name", "price"}`; `201`, returns the new public id |
| `DELETE /items/{public_id}` | `204`; `404` if invalid or unknown |

With the default alphabet in `config.py`, the seeded items get these ids
(yours differ if you set your own `SQIDS_ALPHABET`, so copy them from
`GET /items`):

| Database id | Public id |
|---|---|
| 1 | `igPHZLIU` |
| 2 | `uclL2dH9` |
| 3 | `z67LIUj6` |

```bash
curl http://127.0.0.1:8000/items

curl http://127.0.0.1:8000/items/igPHZLIU

curl http://127.0.0.1:8000/items/1

curl http://127.0.0.1:8000/items/ig

curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Monitor\", \"price\": 199}"

curl -X DELETE http://127.0.0.1:8000/items/z67LIUj6
```

The third and fourth requests are `404 {"detail": "Item not found"}`.
`/items/1` is no longer a valid id at all. `ig` actually *decodes* to 1,
but it isn't the one id we hand out for that row, so it's rejected too
([STEPS.md](STEPS.md) step 4).

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/items`, Body →
raw → JSON:

```json
{"name": "Monitor", "price": 199}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
