# 14/a — The shop API, step by step

Every security idea here was taught on its own in topic 12, and the
order/transaction idea in topic 11. This walkthrough follows a request
through the app instead: set-up, who you are, what you may do, then
products, stock and orders.

## Part 1 — Setup and data

1. **`config.py` — every secret, with dev-only defaults.** Three
   secrets this time: `SECRET_KEY` signs JWTs, `FERNET_KEY` encrypts,
   `SQIDS_ALPHABET` shapes public ids.

   ```python
   SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me-in-production-0123456789")
   FERNET_KEY = os.getenv("FERNET_KEY", "Hq1oQZm3T7V4YkX0sKcN8bWfPuR2dJgLaEyC6iMh5tA=")
   ```

   The defaults are in git, so they're public. They exist only so the
   lesson runs with zero setup. A real shop sets all three in `.env`.

2. **`database.py` — `URL.create` instead of an f-string.**

   ```python
   DATABASE_URL = os.getenv("DATABASE_URL") or URL.create(
       "mysql+pymysql",
       username=MYSQL_USER,
       password=MYSQL_PASSWORD,
       ...
   )
   ```

   With an f-string, a password like `p@ss` gives
   `mysql+pymysql://root:p@ss@127.0.0.1/...`: two `@`, and the driver
   tries to connect to a host called `ss@127.0.0.1`. `URL.create`
   escapes every part for you.

3. **`models.py` — four tables.** `minishop_users` gets a `role` column
   (default `"customer"`). `minishop_products` uses `Numeric(10, 2)` for the
   price, never `Float`, because `0.1 + 0.2` is not `0.3` in floating
   point. `minishop_orders` has many `minishop_order_items` (one-to-many, as in
   11/a). Each item copies the product's price into `unit_price`, so a
   later price change doesn't rewrite what the customer paid.

4. **Encrypted columns, decrypted properties.** An order stores
   `phone_encrypted` and `address_encrypted`. The model adds two
   properties that decrypt them:

   ```python
   @property
   def address(self) -> str:
       return decrypt(self.address_encrypted)
   ```

   `OrderOut` has `phone` and `address` fields and
   `from_attributes=True`, so Pydantic reads these properties and the
   JSON shows real values. The database only ever holds ciphertext.

5. **Hashing vs encryption vs public ids.** Three different tools for
   three different jobs:

   | | Reversible? | Used for | File |
   |---|---|---|---|
   | Hashing (Argon2) | No | Passwords: check them, never read them | `security.py` |
   | Encryption (Fernet) | Yes, with the key | Phone, address: must be read to ship | `encryption.py` |
   | Public ids (Sqids) | Yes, by anyone who knows the alphabet | Hide row counts in URLs | `ids.py` |

   Public ids are **not** security. They stop `/orders/1`, `/orders/2`
   from revealing how many orders exist. The ownership check (step 16)
   is what keeps orders private.

6. **`ids.py` — `PublicId` in schemas, `decode_id` in routes.**

   ```python
   PublicId = Annotated[int, PlainSerializer(encode_id, return_type=str)]
   ```

   A response field typed `id: PublicId` reads the int from the row and
   writes a string like `"Xb3kLq9P"`. Going in, every route calls
   `decode_id(product_id)`, which raises `404` for any string we'd never
   hand out, including `"1"`.

7. **`crud.py` — `seed()`.** Creates `admin`, `alice`, `bob` and four
   products, only when the tables are empty. `create_admin.py` is the
   other way to get an admin, for a real shop with no seed data.

## Part 2 — Who are you, and what may you do?

8. **`/login` returns two tokens.** The access token (15 minutes)
   carries the role:

   ```python
   def create_access_token(username: str, role: str) -> str:
       return _create_token(
           username, "access", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), role=role
       )
   ```

   The role is in the token **only for the frontend**, to pick which
   menu to show. A JWT is signed, not encrypted: anyone can read the
   payload, so never put a secret in it.

9. **`get_current_user` — `401`.** Reads the Bearer token, decodes it,
   then loads the user **from the database**:

   ```python
   username = decode_token(creds.credentials, expected_type="access") if creds else None
   user = crud.get_user_by_username(db, username) if username else None
   ```

   `HTTPBearer(auto_error=False)` lets a missing header fall through to
   our own `401` (FastAPI's default would be `403`, which means
   something else).

10. **`require_roles(...)` — `403`.**

    ```python
    def checker(user: UserModel = Depends(get_current_user)) -> UserModel:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        return user
    ```

    `user.role` comes from the database row, not the token. Promote or
    demote someone and it applies on their very next request. The
    `test_promote_takes_effect_immediately` test proves it.

11. **Three ways to apply it.**

    - One route: `user: UserModel = Depends(require_roles("customer"))`
      on `POST /orders`.
    - A shared variable: `admin_only = require_roles("admin")` in
      `routers/products.py`.
    - A whole router: `APIRouter(..., dependencies=[Depends(require_roles("admin"))])`
      in `routers/users.py`, so no route in that file can forget it.

    `routers/users.py` also refuses to change **your own** role, so the
    last admin can't lock everyone out.

## Part 3 — Products and stock

12. **Customers never see hidden products.**

    ```python
    if product is None or (not product.is_active and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Product not found")
    ```

    `DELETE /products/{id}` only sets `is_active = False` (soft delete,
    11/e). Old orders still point at the product, and an admin can show
    it again with `PATCH {"is_active": true}`.

13. **Stock only moves through `/stock`.** `ProductUpdate` has no
    `stock` field. `PATCH /products/{id}/stock` takes a change (`+10`,
    `-3`) instead of a new value, and locks the row first:

    ```python
    db.refresh(product, with_for_update=True)
    if product.stock + body.change < 0:
        raise HTTPException(status_code=400, detail=f"Only {product.stock} in stock")
    ```

    A change instead of a value matters: if an admin sends "stock = 20"
    while a customer is buying 2, one of the two updates is lost.
    "+10" on a locked row can't lose anything.

## Part 4 — Orders

14. **Placing an order: check everything, then change everything.**
    `place_order` first adds up quantities (the same product twice
    becomes one line), then **locks** every product row in the order:

    ```python
    rows = (
        db.query(ProductModel)
        .filter(ProductModel.id.in_(product_ids))
        .order_by(ProductModel.id)
        .with_for_update()
        .all()
    )
    ```

    `SELECT ... FOR UPDATE` makes any other request that touches these
    rows wait until we commit. Without it, two customers could both read
    "stock: 1", both pass the check, and both buy the last sticker pack.
    Sorting by id means two orders always lock rows in the same order, so
    they can't deadlock waiting for each other.

15. **All or nothing.** Every item is checked before anything changes.
    Any problem raises an exception before `db.commit()`, the session is
    closed, and nothing was written: no order, no stock change (11/d).
    The `test_cannot_oversell` test checks the stock is unchanged after a
    failed order.

16. **Ownership: `404`, not `403`.**

    ```python
    if order is None or (order.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Order not found")
    ```

    A customer asking for someone else's order gets the same answer as
    for an order that doesn't exist, so they can't even learn it exists
    (12/f).

17. **Status flow.** `NEXT_STATUS` lists the allowed moves:

    ```python
    NEXT_STATUS = {
        "pending": {"shipped", "cancelled"},
        "shipped": {"delivered"},
        "delivered": set(),
        "cancelled": set(),
    }
    ```

    Cancelling (by the customer while `pending`, or by an admin) calls
    `restore_stock()`, which locks the products again and puts the
    quantities back.

## Part 5 — Tests

18. **`tests/conftest.py`** sets `DATABASE_URL` to a temporary SQLite
    file **before** importing `main`, so the tests never touch MySQL.
    `TEST_DATABASE_URL` points them at an empty MySQL database instead,
    which also exercises the row locks (SQLite ignores `FOR UPDATE`).

19. **`tests/test_shop.py`** has one test per rule: sign-ups are
    customers, `401` without a token, `403` for the wrong role, public
    ids, stock can't go negative, hidden products, stock restored on
    cancel, no overselling, no peeking at other orders, the status flow,
    and the address being ciphertext in the database.
