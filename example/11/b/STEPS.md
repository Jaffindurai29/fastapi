# 11/b — Nested responses, step by step

`database.py` and `models.py` are exactly the same as
[11/a](../a/STEPS.md), which is why the two can share tables. All the
changes are in `schemas.py` (what the JSON looks like) and `crud.py`
(how the rows are loaded).

1. **`schemas.py` — a field typed as another schema:**

   ```python
   class ItemOut(BaseModel):
       model_config = ConfigDict(from_attributes=True)

       id: int
       name: str
       price: float
       category: CategoryOut
   ```

   With `from_attributes=True`, Pydantic reads `row.category`. That's
   the `relationship()` from 11/a, so it's a `CategoryModel` object, and
   Pydantic converts it into a `CategoryOut` the same way it converts
   the item. The result is a JSON object inside a JSON object.

2. **`schemas.py` — a list of another schema:**

   ```python
   class CategoryWithItems(BaseModel):
       model_config = ConfigDict(from_attributes=True)

       id: int
       name: str
       items: list[ItemSummary]
   ```

   Same idea in the other direction: `row.items` is a list of
   `ItemModel` rows, and each one becomes an `ItemSummary`.

3. **Why `ItemSummary` and not `ItemOut`?** Follow what would happen
   with `items: list[ItemOut]`:

   ```text
   category -> items[0] (ItemOut) -> category -> items[0] -> category -> ...
   ```

   Every item would contain its category, which contains its items,
   which contain the category again. Relationships point both ways, so
   nesting "everything" never ends. Even cut off after one level, it
   repeats the same category inside every item of that category.

   The fix is a second, smaller schema for the inner position:

   ```python
   class ItemSummary(BaseModel):
       model_config = ConfigDict(from_attributes=True)

       id: int
       name: str
       price: float
   ```

   No `category` field. Inside `CategoryWithItems` the category is the
   outer object, so the client already knows it. Rule of thumb: nest in
   **one direction per response**, and give the inner objects a schema
   without the back-reference.

4. **The N+1 problem.** Look at what plain lazy loading does for
   `GET /items` with a query like 11/a's:

   ```python
   rows = db.query(ItemModel).all()   # 1 query: SELECT ... FROM rel_items
   ```

   Then Pydantic builds each `ItemOut` and reads `row.category`. The
   category wasn't loaded, so SQLAlchemy runs **another** query, right
   there, for that item:

   ```text
   SELECT ... FROM rel_items                          -- 1
   SELECT ... FROM rel_categories WHERE id = 1        -- for Laptop
   SELECT ... FROM rel_categories WHERE id = 2        -- for FastAPI Guide
   ...one more per different category...
   ```

   That's **1 query for the list + up to N queries for the related
   rows**, hence "N+1". (SQLAlchemy skips a lookup when that category is
   already loaded, so with the 4 seeded items in 2 categories it's
   1 + 2 = 3 queries.) With 500 items in 500 categories it's 501
   queries for one request, each one a round trip to MySQL. The other
   direction, a list of categories each reading `.items`, is always
   exactly 1 + one per category.

   Nothing errors and the JSON is correct, which is why it's easy to
   miss. It only shows up as "this endpoint got slow".

5. **`crud.py` — `selectinload` fixes it with one extra query:**

   ```python
   return (
       db.query(ItemModel)
       .options(selectinload(ItemModel.category))
       .order_by(ItemModel.id)
       .all()
   )
   ```

   ```text
   SELECT ... FROM rel_items ORDER BY id                       -- 1
   SELECT ... FROM rel_categories WHERE id IN (1, 2)           -- 2
   ```

   It collects every `category_id` from the first result and fetches
   them all at once. **2 queries total** whether there are 4 items or
   4000. When Pydantic then reads `row.category`, it's already there.

6. **`crud.py` — `joinedload` does it in a single query:**

   ```python
   return (
       db.query(ItemModel)
       .options(joinedload(ItemModel.category))
       .filter(ItemModel.id == item_id)
       .first()
   )
   ```

   ```text
   SELECT ... FROM rel_items LEFT OUTER JOIN rel_categories ON ... WHERE rel_items.id = ?
   ```

   One query, because the category columns come back on the same row.
   Which one to pick:
   - **`joinedload`** for "many-to-one" (an item's single category),
     especially for one row. The JOIN adds a few columns, nothing more.
   - **`selectinload`** for "one-to-many" lists (a category's items).
     A JOIN there would repeat the category's columns on every item row;
     the `IN (...)` query avoids that.

7. **`crud.py` — the category page uses `selectinload`:**

   ```python
   return (
       db.query(CategoryModel)
       .options(selectinload(CategoryModel.items))
       .filter(CategoryModel.id == category_id)
       .first()
   )
   ```

   2 queries: the category, then its items.

8. **How to see the queries yourself.** Pass `echo=True` to
   `create_engine` in `database.py` and every SQL statement is printed in
   the uvicorn console. Remove `.options(...)` from `get_items`, call
   `GET /items`, and count the `SELECT`s; put it back and count again.
   Don't leave `echo=True` on in real use: it logs every query.
