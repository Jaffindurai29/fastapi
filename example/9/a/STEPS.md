# 9/a — skip/limit pagination, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md), and the same
`response_model` + `ItemOut` pattern as [8/d](../../8/d). What's new is
two function arguments and two query methods.

1. **`models.py` — a catalog worth paging through.** One table,
   `catalog_items`, shared by all of 9/a–9/d:

   ```python
   name = Column(String(100), nullable=False)
   category = Column(String(50), nullable=False)
   price = Column(Float, nullable=False)
   created_at = Column(DateTime, nullable=False, server_default=func.now())
   ```

   `crud.seed_items` inserts 25 rows across five categories the first
   time the table is empty, so pages and filters have visible effects.

2. **`main.py` — query parameters are just function arguments.**

   ```python
   @app.get("/items", response_model=list[ItemOut])
   def list_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
       return crud.get_items(db, skip=skip, limit=limit)
   ```

   `skip` and `limit` aren't in the path (`/items` has no `{...}`), so
   FastAPI looks for them in the **query string**, the part after `?`.
   The rule is simple: a function argument that isn't a path parameter,
   isn't a Pydantic body model, and isn't a `Depends` is a query
   parameter.

   - The `= 0` / `= 10` defaults make them optional. Leave them off and
     you get the first 10 rows.
   - The `int` type is enforced the same way it is for path parameters
     ([8/a](../../8/a/STEPS.md), step 5): `?limit=ten` is a `422`
     before your code runs, and `?limit=5` arrives as the integer `5`,
     not the string `"5"`.

3. **`crud.py` — `offset` and `limit` become SQL.**

   ```python
   return (
       db.query(ItemModel)
       .order_by(ItemModel.id)
       .offset(skip)
       .limit(limit)
       .all()
   )
   ```

   This becomes `SELECT ... ORDER BY id LIMIT 5 OFFSET 10`. The
   database does the cutting, so only 5 rows ever leave MySQL. Fetching
   everything and slicing a Python list would work too, but would read
   the whole table on every request.

4. **Always `order_by` before paging.** SQL tables have **no built-in
   order**. Without `ORDER BY`, the database returns rows in whatever
   order is cheapest for it right now, and that can change between two
   requests (after an insert, a delete, or just a different query plan).
   So "skip 10, take 10" could hand you a row you already saw on page 1
   and silently skip another. Sorting by a unique column (`id`) makes
   every page well-defined: page 2 always starts exactly where page 1
   ended.

5. **Past the end is not an error.** `?skip=100` on a 25-row table
   gives `[]`. The query ran fine; there just weren't any rows there. An
   empty list is the honest answer.

6. **Why unbounded lists are a problem.** Before this lesson, `GET
   /items` returned every row. With 25 rows nobody notices. With a
   million, one request loads a million rows into memory, turns them
   into JSON, and sends megabytes over the network. Do that a few times
   at once and the server falls over. Pagination makes the cost of a
   request **fixed** (at most `limit` rows), no matter how big the table
   grows.

7. **What's still missing.** Nothing stops `?limit=1000000` (the
   unbounded list is back), and negative numbers aren't refused either:
   SQLite quietly ignores `?skip=-1`, while MySQL rejects the SQL and
   you get a `500`. [9/c](../c/STEPS.md) adds `ge`/`le` rules to fix
   both. First, [9/b](../b/STEPS.md) adds filtering and sorting.
