# 11/d — Transactions, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md). Note one line in it
that has been there since topic 6:

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

`autocommit=False` means nothing is permanent until you call
`db.commit()`. Every route so far did one change and committed. This one
does many changes, and when to commit becomes the whole lesson.

1. **What a transaction is.** The database groups every statement since
   the last commit into one unit. Then it either:
   - **commits**: all of them become permanent, together, and other
     connections can see them; or
   - **rolls back**: all of them are undone, as if they never ran.

   That's **atomicity**, the "A" in ACID: a transaction can't half
   happen. MySQL's InnoDB engine (the default) and SQLite both support
   it.

2. **`models.py` — three tables:**

   ```python
   class OrderLineModel(Base):
       __tablename__ = "shop_order_lines"

       id = Column(Integer, primary_key=True, autoincrement=True)
       order_id = Column(Integer, ForeignKey("shop_orders.id"), nullable=False)
       product_id = Column(Integer, ForeignKey("shop_products.id"), nullable=False)
       quantity = Column(Integer, nullable=False)
       # Copied from the product at order time. If the price changes next
       # week, this order still shows what the customer actually paid.
       unit_price = Column(Float, nullable=False)
   ```

   An order has many lines (one-to-many, like [11/a](../a/STEPS.md)).
   `unit_price` is **copied** from the product when the order is placed,
   so changing a price next week doesn't rewrite old orders.

3. **`schemas.py` — at least one line, at least 1 of each:**

   ```python
   class OrderLineIn(BaseModel):
       product_id: int
       quantity: int = Field(gt=0)


   class OrderCreate(BaseModel):
       # An order with no lines makes no sense: at least one.
       lines: list[OrderLineIn] = Field(min_length=1)
   ```

   Shape errors are a `422` before any database work starts
   ([8/a](../../8/a/STEPS.md)).

4. **`crud.py` — the checks every line goes through:**

   ```python
   def _take_from_stock(db: Session, line: OrderLineIn) -> ProductModel:
       # Shared by both versions: check the product, then decrement stock.
       product = db.get(ProductModel, line.product_id)
       if product is None:
           raise OrderError(404, f"Product {line.product_id} not found")
       if product.stock < line.quantity:
           raise OrderError(
               409,
               f"Not enough stock for {product.name}: "
               f"wanted {line.quantity}, have {product.stock}",
           )
       product.stock -= line.quantity
       return product
   ```

   `OrderError` is a plain Python exception that carries a status code.
   `crud.py` stays free of FastAPI; the router turns it into an
   `HTTPException`. The same product twice in one order works too:
   `db.get` returns the same object both times, so the second check sees
   the stock the first line already took.

5. **`crud.py` — the safe version: one commit, at the end:**

   ```python
   try:
       order = OrderModel(total=0)
       db.add(order)
       # flush() sends the INSERT now (so order.id exists) but does NOT
       # commit. It's still inside the transaction and can be undone.
       db.flush()

       total = 0.0
       for line in data.lines:
           product = _take_from_stock(db, line)  # may raise
           order.lines.append(
               OrderLineModel(
                   product_id=product.id,
                   quantity=line.quantity,
                   unit_price=product.price,
               )
           )
           total += product.price * line.quantity

       order.total = round(total, 2)
       db.commit()  # the only commit: everything becomes permanent together
   except Exception:
       # Anything went wrong: throw away EVERY change since the last
       # commit. The order row, its lines, and every stock decrement.
       db.rollback()
       raise
   ```

   - `db.flush()` sends the order's `INSERT` to the database now (so it
     gets an `id`) but **doesn't commit**. It's inside the transaction
     and can still be undone. Flush = "send the SQL", commit = "make it
     permanent".
   - If line 2 fails, the order `INSERT`, line 1, and line 1's stock
     decrement are all still uncommitted. `db.rollback()` throws every
     one of them away. The database looks exactly as it did before the
     request.
   - `except Exception` (not just `OrderError`) so that **any** failure,
     even a bug or a lost connection, also rolls back. Then `raise`
     passes the error on unchanged.
   - Only if the loop finishes does `db.commit()` run, and then the
     order, all its lines and all the stock changes appear together.

6. **`crud.py` — the unsafe version: a commit per step:**

   ```python
   order = OrderModel(total=0)
   db.add(order)
   db.commit()  # the empty order is now permanent

   for line in data.lines:
       product = _take_from_stock(db, line)  # may raise...
       order.lines.append(...)
       order.total = round(order.total + product.price * line.quantity, 2)
       db.commit()  # ...but every line before it is already committed
   ```

   Same checks, same error codes. The difference: by the time line 2
   fails, the order and line 1 (with its stock decrement) are already
   committed. A `rollback()` here would only undo the current, failing
   line. The earlier commits are permanent. That's the half-built order
   and the missing keyboards in the [README](README.md#see-the-bug).

   Committing per step looks harmless when every request succeeds. It
   only breaks on the failure path, which is exactly the path you test
   least.

7. **`routers/orders.py` — translating the error:**

   ```python
   @router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
   def create_order(data: OrderCreate, db: Session = Depends(get_db)):
       try:
           return crud.place_order(db, data)
       except crud.OrderError as exc:
           # crud already rolled back; just turn it into an HTTP answer.
           raise HTTPException(status_code=exc.status_code, detail=exc.message)
   ```

8. **Why not let `get_db` handle it?** `get_db` closes the session in
   `finally`, and closing a session with uncommitted changes discards
   them, so an un-committed failure is rolled back eventually anyway.
   Calling `db.rollback()` yourself makes it explicit and immediate, and
   leaves the session usable if the route wanted to carry on (say, to
   log the failed attempt).

9. **The alternative: `with db.begin():`.** SQLAlchemy can do the
   try/commit/except/rollback for you:

   ```python
   with db.begin():
       ...  # all the work
   # leaving the block normally -> commit
   # an exception inside the block -> rollback, then re-raise
   ```

   It's shorter and you can't forget the rollback. The catch: it must be
   the **first** thing that touches the session, because SQLAlchemy 2.0
   starts a transaction automatically on the first query, and
   `db.begin()` on a session that already has one raises an error. In a
   route that has already looked something up, the explicit
   `try`/`commit`/`rollback` used here is simpler to reason about.

10. **What a transaction doesn't solve on its own.** Two requests at the
    same moment can both read "Monitor stock = 1", both pass the check,
    and both decrement. Fixing that means locking the row while you
    check it (`db.query(ProductModel).with_for_update()` on MySQL) or an
    atomic `UPDATE ... SET stock = stock - 1 WHERE stock >= 1`. That's
    concurrency, a separate topic; this lesson is about all-or-nothing.
