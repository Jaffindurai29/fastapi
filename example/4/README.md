# 4 — Array + CRUD

All five HTTP verbs over a small in-memory array, one per sub-topic —
each seeded with two starting items so it's testable on its own.

| Sub-topic | Verb | What it covers |
|---|---|---|
| [4/a — GET](a) | `GET` | List the whole array, or reach one item by index. |
| [4/b — POST](b) | `POST` | Add a new item to the end. |
| [4/c — PUT](c) | `PUT` | Replace an item at a given index entirely. |
| [4/d — PATCH](d) | `PATCH` | Partially update an item — the field is optional. |
| [4/e — DELETE](e) | `DELETE` | Remove an item at a given index. |

Each folder above has its own **README.md** (how to run it, routes,
`curl`/Postman) and **STEPS.md** (line-by-line code walkthrough).

Want to call this from a browser? See [5 — React + Array + CRUD](../5), which adds
CORS and a real frontend covering all five verbs on top of this same
shape.
