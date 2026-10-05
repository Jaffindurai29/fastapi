# 8/a — Field validation, step by step

Same `database.py` as [6/a](../../6/a/STEPS.md). What's new is all in
`schemas.py`, and `main.py` gets the payoff for free.

1. **`models.py` — three columns instead of one**, and `name` is
   `unique=True`, so the database itself refuses a second "Laptop":

   ```python
   name = Column(String(50), nullable=False, unique=True)
   price = Column(Float, nullable=False)
   quantity = Column(Integer, nullable=False, default=0)
   ```

2. **`schemas.py` — `Field(...)` adds rules on top of the type:**

   ```python
   class ItemCreate(BaseModel):
       name: str = Field(min_length=1, max_length=50)
       price: float = Field(gt=0, le=1_000_000)
       quantity: int = Field(default=0, ge=0)
   ```

   `gt` = greater than, `ge` = greater or equal, `lt`/`le` the same for
   "less than". `min_length`/`max_length` work on strings (and lists).
   `quantity` has a default, so it's optional in the request. `name` and
   `price` don't, so they're required.

3. **`schemas.py` — `@field_validator` for rules `Field` can't express:**

   ```python
   @field_validator("name")
   @classmethod
   def name_not_blank(cls, value: str) -> str:
       value = value.strip()
       if value == "":
           raise ValueError("name must not be blank")
       return value
   ```

   `"   "` is 3 characters, so it passes `min_length=1`, but it's still
   blank. The validator runs **after** the type and `Field` checks. A
   `ValueError` raised here becomes one more entry in the `422` list.
   Whatever it **returns** is the value your route sees, so `"  Desk "`
   is stored as `"Desk"`.

4. **`main.py` — no validation code at all.** The route just declares
   `item: ItemCreate`:

   ```python
   @app.post("/items", status_code=status.HTTP_201_CREATED)
   def create_item(item: ItemCreate, db: Session = Depends(get_db)):
       return to_dict(crud.create_item(db, item))
   ```

   If the body breaks any rule, this function is **never called**.
   FastAPI answers `422` on its own. Inside the function, every field is
   guaranteed to be valid.

5. **Path parameters are validated too.** `item_id: int` means
   `/items/abc` gets a `422` (`int_parsing`) without your code running.

6. **Reading a `422` response.** Each entry in `detail` has:
   - `loc`: where the problem is (`["body", "price"]`,
     `["path", "item_id"]`)
   - `msg`: a human-readable reason
   - `type`: a machine-readable reason (`greater_than`, `missing`,
     `string_too_long`, ...)

   All failures are reported at once, not just the first one.

7. **What validation *can't* catch: duplicates.** Pydantic only sees the
   request. It doesn't know what's already in the database. So posting
   "Laptop" twice passes validation, hits the `unique` column, and
   crashes with a `500`. Checking against stored data is the route's
   job, and that's [8/b](../b/STEPS.md).
