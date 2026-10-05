# 11/a — One-to-many, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md). The `routers/` layout
is the one from [10/a](../../10/a/STEPS.md): one module per resource,
`main.py` only plugs them in. What's new is two tables that are linked.

1. **`models.py` — the foreign key is a real column on the "many"
   side:**

   ```python
   category_id = Column(Integer, ForeignKey("rel_categories.id"), nullable=False)
   ```

   Each item row stores the `id` of its category. `ForeignKey(...)`
   tells the database "this value must match an `id` in
   `rel_categories`". `nullable=False` means an item can't exist
   without a category. The link always lives on the "many" side: a
   category row can't hold a list of item ids, but each item can hold
   one category id.

2. **`models.py` — `relationship()` is the Python-side shortcut:**

   ```python
   # on CategoryModel
   items = relationship("ItemModel", back_populates="category")

   # on ItemModel
   category = relationship("CategoryModel", back_populates="items")
   ```

   These are **not** columns. Nothing is added to either table.
   `category.items` gives you a list of `ItemModel` rows (SQLAlchemy runs
   `SELECT ... FROM rel_items WHERE category_id = ?` the first time you
   touch it). `item.category` gives you the `CategoryModel` row.
   `back_populates` names the attribute on the *other* class, so the two
   stay in sync in memory: set `item.category = books` and `item` also
   appears in `books.items`.

3. **`crud.py` — the seed uses the relationship instead of ids:**

   ```python
   electronics = CategoryModel(name="Electronics")
   books = CategoryModel(name="Books")
   # Setting the relationship (category=...) instead of category_id:
   # SQLAlchemy inserts the category first, then fills in the id.
   db.add_all(
       [
           ItemModel(name="Laptop", price=999.99, category=electronics),
           ...
   ```

   The categories don't have ids yet (they're not in the database). By
   passing `category=electronics`, SQLAlchemy works out the order:
   insert the categories first, read back their new ids, then insert the
   items with the right `category_id`. You never touch an id by hand.

4. **`main.py` — `create_all` gets the order right too.** It sees that
   `rel_items` has a foreign key to `rel_categories`, so it creates
   `rel_categories` first. `main.py` itself only builds the app and
   includes the two routers:

   ```python
   app.include_router(categories.router)
   app.include_router(items.router)
   ```

5. **`routers/items.py` — check the foreign key yourself:**

   ```python
   if crud.get_category(db, item.category_id) is None:
       raise HTTPException(
           status_code=404,
           detail=f"Category {item.category_id} not found",
       )
   return crud.create_item(db, item)
   ```

   Why not let the database catch it? Because what happens depends on
   the database:
   - **MySQL (InnoDB)** enforces foreign keys. The `INSERT` fails with an
     `IntegrityError`, which nobody catches, so the client gets a `500`.
   - **SQLite** does **not** enforce foreign keys unless you turn them on
     (`PRAGMA foreign_keys = ON`) for every connection. It would happily
     store `category_id = 999`, pointing at nothing.

   One lookup first gives a clear `404` on both. The database constraint
   stays as the safety net. `404` (not `400` or `422`) because the body
   is well-formed; it refers to something that doesn't exist, the same
   way `GET /categories/999` would.

6. **`routers/categories.py` — `404` vs an empty list:**

   ```python
   if crud.get_category(db, category_id) is None:
       raise HTTPException(status_code=404, detail="Category not found")
   return crud.get_items_in_category(db, category_id)
   ```

   Without the first check, `/categories/999/items` would return `[]`,
   and the client couldn't tell "no such category" from "category with
   no items yet". Same idea as `GET /items/{id}` from earlier topics.

7. **`routers/categories.py` — refuse to orphan children:**

   ```python
   count = crud.count_items_in_category(db, category_id)
   if count > 0:
       raise HTTPException(
           status_code=409,
           detail=f"Category still has {count} item(s); move or delete them first",
       )
   crud.delete_category(db, row)
   ```

   Deleting "Electronics" while the Laptop still points at it would
   leave `category_id = 1` aimed at nothing (on SQLite) or crash with an
   `IntegrityError` (on MySQL). `409 Conflict` says "the request is fine,
   but the current state of the data doesn't allow it", the same code
   [8/b](../../8/b/STEPS.md) used for a duplicate name. The other common
   choices are cascading (delete the items too:
   `relationship(..., cascade="all, delete-orphan")`) or `SET NULL`
   (only possible if `category_id` is nullable). Refusing is the safest
   default: nothing disappears by surprise.

8. **`schemas.py` — flat responses:**

   ```python
   class ItemOut(BaseModel):
       model_config = ConfigDict(from_attributes=True)

       id: int
       name: str
       price: float
       category_id: int
   ```

   The item points at its category by id. If the client wants the
   category's name it has to make a second call. [11/b](../b/STEPS.md)
   nests the category inside the item instead, and that turns out to
   need some care.
