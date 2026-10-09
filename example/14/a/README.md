# 14/a — Shop API

A small online shop: products with stock, orders with line items, and
two roles (`customer`, `admin`). It uses almost everything from topics
11 and 12 at once:

| Idea | From | Where in this app |
|---|---|---|
| Password hashing (Argon2) | [12/a](../../12/a) | `security.py` |
| JWT access + refresh tokens | [12/b](../../12/b), [12/d](../../12/d) | `security.py`, `routers/auth.py` |
| Roles, `401` vs `403` | [12/e](../../12/e) | `dependencies.py` (`require_roles`) |
| Ownership ("only your own orders") | [12/f](../../12/f) | `routers/orders.py` (`get_order_or_404`) |
| Encryption (phone, address) | [12/g](../../12/g) | `encryption.py`, `models.py` |
| Public ids instead of 1, 2, 3 | [12/h](../../12/h) | `ids.py`, `schemas.py` |
| One-to-many, nested responses | [11/a](../../11/a), [11/b](../../11/b) | orders → order items |
| All-or-nothing transactions | [11/d](../../11/d) | `routers/orders.py` (`place_order`) |
| Soft delete | [11/e](../../11/e) | products are hidden, never deleted |

New here: **row locks** (`SELECT ... FOR UPDATE`) so two customers can't
both buy the last item. [STEPS.md](STEPS.md) walks through the code.

Same [setup](../../6/a/README.md#setup) as topic 6 (database, `.env`,
SQLite fallback). Every setting in `.env.example` has a development
default, so it runs with zero setup.

## Files

| File | Responsibility |
|---|---|
| `config.py` | secrets and settings from env / `.env`, with dev-only defaults |
| `database.py` | `engine`, `SessionLocal`, `Base`, `get_db()` (`URL.create`, so `@` in a password is safe) |
| `models.py` | `minishop_users`, `minishop_products`, `minishop_orders`, `minishop_order_items` |
| `schemas.py` | request bodies and `*Out` response models (public ids, decrypted address) |
| `security.py` | password hashing, creating and decoding JWTs |
| `encryption.py` | Fernet `encrypt()` / `decrypt()` |
| `ids.py` | `encode_id()` / `decode_id()` with Sqids, `PublicId` type |
| `crud.py` | user functions + demo seed data |
| `dependencies.py` | `get_current_user` (`401`), `require_roles(...)` (`403`) |
| `routers/auth.py` | `/register`, `/login`, `/refresh`, `/me` |
| `routers/products.py` | product list/detail, admin CRUD, stock changes |
| `routers/orders.py` | place, list, cancel orders; admin status changes |
| `routers/users.py` | admin: list users, change roles |
| `main.py` | creates tables, seeds, CORS, includes the routers |
| `create_admin.py` | promote or create an admin from the command line |
| `tests/` | 14 pytest tests for the rules below |

## Run it

```bash
pip install fastapi "uvicorn[standard]" sqlalchemy pymysql python-dotenv "pwdlib[argon2]" pyjwt cryptography sqids
cd example/14/a
uvicorn main:app --reload
```

Seeded on the first run (only when the tables are empty):

| Username | Password | Role |
|---|---|---|
| `admin` | `admin-password` | admin |
| `alice` | `alice-password` | customer |
| `bob` | `bob-password` | customer |

...plus four products. "Sticker pack" has a stock of **1**, so you can
watch the second order for it fail.

### Your own admin: `create_admin.py`

Sign-ups through the API are always customers. On a real shop there's no
seed data, so the first admin is made from the command line:

```bash
python create_admin.py carol
```

If `carol` exists, she's promoted. If not, you're asked for a password
and the account is created as an admin.

## Routes

| Route | Who | Description |
|---|---|---|
| `POST /register` | anyone | `{"username", "password"}`. `201`, always role `customer`. `409` if taken |
| `POST /login` | anyone | `{"username", "password"}`. Returns `access_token` + `refresh_token`. `401` otherwise |
| `POST /refresh` | anyone | `{"refresh_token"}`. Returns a new access token |
| `GET /me` | logged in | Your public id, username, role |
| `GET /products` | logged in | Customers: visible products. Admins: all, including hidden |
| `GET /products/{id}` | logged in | `404` for a hidden product (customers) or an id we never handed out |
| `POST /products` | admin | `{"name", "description", "price", "stock"}`. `201` |
| `PATCH /products/{id}` | admin | Any of `name`, `description`, `price`, `is_active` |
| `PATCH /products/{id}/stock` | admin | `{"change": 10}` or `{"change": -3}`. `400` if stock would go below 0 |
| `DELETE /products/{id}` | admin | Hides the product (`204`). Old orders still show it |
| `POST /orders` | customer | `{"items": [{"product_id", "quantity"}], "phone", "address"}`. `201`, `409` "Only 1 of ... left" |
| `GET /orders/mine` | logged in | Your orders, newest first |
| `GET /orders/{id}` | logged in | `404` if it isn't yours (admins see all) |
| `POST /orders/{id}/cancel` | logged in | Only `pending` orders (`400` otherwise). Stock goes back |
| `GET /orders` | admin | Every order, with decrypted phone and address |
| `PATCH /orders/{id}/status` | admin | `pending → shipped → delivered`, or `pending → cancelled`. `400` for anything else |
| `GET /users` | admin | Every user |
| `PATCH /users/{id}/role` | admin | `{"role": "admin"}` or `{"role": "customer"}`. `400` for your own account |

No token or an expired one → `401`. Logged in but the wrong role → `403`.

## Try it with curl

```bash
curl -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" -d "{\"username\": \"alice\", \"password\": \"alice-password\"}"
```

Copy `access_token` and use it in place of `TOKEN`:

```bash
curl http://127.0.0.1:8000/products -H "Authorization: Bearer TOKEN"
```

The ids look like `"id": "Xb3kLq9P"`. Use one as `PRODUCT_ID`:

```bash
curl -X POST http://127.0.0.1:8000/orders -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d "{\"items\": [{\"product_id\": \"PRODUCT_ID\", \"quantity\": 1}], \"phone\": \"0300-1234567\", \"address\": \"12 Main Street\"}"
```

Things worth trying:

- As `alice`, `GET /orders` → `403` (admin only). `GET /products/1` →
  `404` (not an id we ever hand out).
- Order the "Sticker pack" twice → the second answer is `409` "Only 0 of
  Sticker pack left", and nothing about the order was saved.
- As `bob`, open one of alice's order ids → `404`, not `403`: bob isn't
  even told it exists.
- Look in MySQL: `SELECT phone_encrypted, address_encrypted FROM
  minishop_orders;` shows ciphertext like `gAAAAABm...`. The API shows the
  real values to the owner and admins.
- As `admin`, promote `bob` with `PATCH /users/{id}/role`. Bob's **old**
  token now works on admin routes immediately: the role is read from the
  database, not from the token.

Or click **Authorize** in `/docs` and paste an `access_token`.

## Tests

```bash
pip install pytest httpx
cd example/14/a
pytest tests
```

They run against a throwaway SQLite file, never your MySQL data. SQLite
ignores row locks, so to test those too, point them at an **empty**
MySQL database:

```bash
TEST_DATABASE_URL="mysql+pymysql://root:your-password@127.0.0.1:3306/shop_test" pytest tests
```
