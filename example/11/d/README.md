# 11/d — Transactions

Placing an order touches several rows: one order, one line per product,
and every product's stock. Either **all** of that is saved or **none**
of it is. `POST /orders` does the whole job in one transaction, commits
once at the end, and rolls back on any error. `POST /orders/unsafe`
takes the same input but commits after every step, and shows what that
breaks. See [STEPS.md](STEPS.md) for the walkthrough.

Same [setup](../../6/a/README.md#setup) as topic 6, and the `routers/`
layout from [10/a](../../10/a). Own tables: `shop_products`,
`shop_orders`, `shop_order_lines`. Seeded with Keyboard (50.0, stock
10), Mouse (20.0, stock 5) and Monitor (200.0, stock 1).

```bash
cd example/11/d
uvicorn main:app --reload
```

| Route | Status | Description |
|---|---|---|
| `GET /products` | `200` | Every product with its current `stock` |
| `GET /products/{product_id}` | `200`, `404` | One product |
| `POST /orders` | `201`, `404`, `409`, `422` | Place an order, all-or-nothing |
| `POST /orders/unsafe` | `201`, `404`, `409`, `422` | Same, but commits line by line (the bug) |
| `GET /orders` | `200` | Every order with its lines |
| `GET /orders/{order_id}` | `200`, `404` | One order with its lines |

`404` = a `product_id` doesn't exist. `409` = not enough stock. `422` =
empty `lines` or a `quantity` below 1.

```bash
curl -X POST http://127.0.0.1:8000/orders -H "Content-Type: application/json" -d "{\"lines\": [{\"product_id\": 1, \"quantity\": 2}, {\"product_id\": 2, \"quantity\": 1}]}"
```

```json
{"id": 1, "created_at": "2026-10-05T10:27:53", "total": 120.0, "lines": [{"id": 1, "product_id": 1, "quantity": 2, "unit_price": 50.0}, {"id": 2, "product_id": 2, "quantity": 1, "unit_price": 20.0}]}
```

## See the bug

Order 3 Keyboards and 5 Monitors. There's only 1 Monitor, so the
**second** line fails. Send it to the safe endpoint first:

```bash
curl -X POST http://127.0.0.1:8000/orders -H "Content-Type: application/json" -d "{\"lines\": [{\"product_id\": 1, \"quantity\": 3}, {\"product_id\": 3, \"quantity\": 5}]}"

curl http://127.0.0.1:8000/products
curl http://127.0.0.1:8000/orders
```

`409 {"detail": "Not enough stock for Monitor: wanted 5, have 1"}`.
Keyboard stock is still 8 and there's still only one order. Nothing was
written.

Now the exact same body to the unsafe endpoint:

```bash
curl -X POST http://127.0.0.1:8000/orders/unsafe -H "Content-Type: application/json" -d "{\"lines\": [{\"product_id\": 1, \"quantity\": 3}, {\"product_id\": 3, \"quantity\": 5}]}"

curl http://127.0.0.1:8000/products
curl http://127.0.0.1:8000/orders
```

Same `409`, so the client thinks the order failed. But Keyboard stock
dropped from 8 to **5**, and `GET /orders` lists a new, half-built
order:

```json
{"id": 2, "created_at": "2026-10-05T10:27:53", "total": 150.0, "lines": [{"id": 3, "product_id": 1, "quantity": 3, "unit_price": 50.0}]}
```

Three keyboards are gone from stock for an order nobody placed.

**Postman:** Method `POST`, URL `http://127.0.0.1:8000/orders` (or
`.../orders/unsafe`), Body → raw → JSON:

```json
{"lines": [{"product_id": 1, "quantity": 3}, {"product_id": 3, "quantity": 5}]}
```

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
