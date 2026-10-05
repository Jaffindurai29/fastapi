# 9/b — Search, filter, sort, step by step

Same `database.py`, `models.py` and `schemas.py` as [9/a](../a/STEPS.md).
`main.py` gets more parameters; `crud.py` gets a query that's built up
piece by piece.

1. **`main.py` — optional parameters default to `None`.**

   ```python
   def list_items(
       search: str | None = None,
       category: str | None = None,
       min_price: float | None = None,
       max_price: float | None = None,
       sort_by: Literal["id", "name", "price", "created_at"] = "id",
       order: Literal["asc", "desc"] = "asc",
       skip: int = 0,
       limit: int = 10,
       db: Session = Depends(get_db),
   ):
   ```

   `None` means "the client didn't send this one". That's different from
   an empty or zero value: `?min_price=0` is a real filter, missing
   `min_price` is no filter. The types still apply when a value *is*
   sent: `?min_price=cheap` is a `422` (`float_parsing`).

2. **`crud.py` — start broad, narrow step by step.**

   ```python
   query = db.query(ItemModel)

   # Only add a filter when the client actually sent that parameter.
   if search is not None:
       # ilike = case-insensitive LIKE. %...% means "contains".
       query = query.filter(ItemModel.name.ilike(f"%{search}%"))
   if category is not None:
       query = query.filter(ItemModel.category == category)
   if min_price is not None:
       query = query.filter(ItemModel.price >= min_price)
   if max_price is not None:
       query = query.filter(ItemModel.price <= max_price)
   ```

   `db.query(...)` doesn't touch the database yet. It's a **description**
   of a query. Each `.filter(...)` returns a new description with one
   more `WHERE` condition, joined with `AND`. Nothing runs until `.all()`
   at the very end, so building it in six steps costs the same as
   writing it in one line.

   The `if ... is not None` checks are the whole trick. Without them
   you'd need a separate query for every combination of filters (16 for
   four filters). With them, one function handles all of them.

3. **`ilike` — case-insensitive "contains".** `LIKE '%chef%'` matches
   any name with `chef` somewhere inside; `%` means "any characters".
   `ilike` ignores case, so `chef`, `CHEF` and `Chef` all find
   `Chef's Knife`. SQLAlchemy turns it into whatever the database
   understands (`lower(name) LIKE lower(...)` on MySQL).

   The search text is sent as a **bound parameter**, not pasted into the
   SQL string, so `?search=' OR 1=1 --` is just a strange name to look
   for, not SQL injection. A `%` or `_` typed by the user still acts as
   a wildcard inside the pattern, which is harmless here.

4. **`sort_by` — why `Literal`, not `str`.**

   ```python
   sort_by: Literal["id", "name", "price", "created_at"] = "id",
   order: Literal["asc", "desc"] = "asc",
   ```

   `Literal[...]` is a **whitelist**. FastAPI checks the value against
   the list and answers `422` for anything else, so `crud.py` only ever
   sees one of those four strings. That matters because the sort column
   comes from the user, and the column name can't be a bound parameter
   the way a search value can. Two safe rules follow:

   - never pass a user string to `order_by()` (`order_by(text(sort_by))`
     would let a client sort by a column you never meant to expose, or
     worse, inject SQL);
   - map the whitelisted name to a real column yourself:

   ```python
   SORT_COLUMNS = {
       "id": ItemModel.id,
       "name": ItemModel.name,
       "price": ItemModel.price,
       "created_at": ItemModel.created_at,
   }
   ```

   Bonus: `/docs` shows `sort_by` and `order` as dropdowns, because it
   knows every allowed value.

5. **`crud.py` — sort, with a tie-breaker, then page.**

   ```python
   column = SORT_COLUMNS[sort_by]
   column = column.desc() if order == "desc" else column.asc()
   # id as a tie-breaker: rows with the same price (or created_at) still
   # come back in a fixed order, so pages never overlap.
   query = query.order_by(column, ItemModel.id)

   return query.offset(skip).limit(limit).all()
   ```

   The 9/a rule ("order before paging") needs a **unique** order to
   work. All 25 seed rows have the same `created_at` (they were inserted
   together), so `ORDER BY created_at` alone leaves their order up to
   the database again. Adding `id` as a second sort key breaks every
   tie.

   Order of operations matters: filter, then sort, then page. Paging
   first would mean "take 10 rows, then filter them", which could leave
   you with 2.

6. **Combinations are free.**
   `?category=electronics&max_price=100&sort_by=price` adds two `WHERE`
   conditions and one `ORDER BY`. No new code is needed for any mix of
   parameters.

7. **What's still missing.** `?limit=1000000` still returns everything,
   `?search=a` matches almost every row, and you can only pick one
   category. [9/c](../c/STEPS.md) adds rules to each parameter with
   `Query(...)`.
