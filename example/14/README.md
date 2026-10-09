# 14 — Shop project (capstone)

Topics 11 and 12 taught one idea at a time: relationships and
transactions, then hashing, JWT, roles, ownership, encryption and ID
hashing. This topic puts them all into one real app, a small online
shop with two roles:

| | Customer | Admin |
|---|:-:|:-:|
| Browse products | ✅ | ✅ (also sees hidden ones) |
| Place an order, see and cancel **own** orders | ✅ | — |
| Add / edit / hide products, change stock | — | ✅ |
| See **all** orders, change order status | — | ✅ |
| List users, change roles | — | ✅ |

| Sub-topic | What it covers |
|---|---|
| [14/a — Shop API](a) | Products, stock, orders with a row-locked transaction, roles, encrypted address, public ids, 14 pytest tests. |
| [14/react — Shop UI](react) | React Router with role-protected routes, a role-based navbar, an axios refresh interceptor, shop and admin pages. |

Same [setup](../6/a/README.md#setup) as topic 6 (database, `.env`,
SQLite fallback). Each folder has its own **README.md** and **STEPS.md**.

14/a uses its own tables (`minishop_users`, `minishop_products`, `minishop_orders`,
`minishop_order_items`), so it's safe to run in the same `fastapi_learn`
database as every other topic.
