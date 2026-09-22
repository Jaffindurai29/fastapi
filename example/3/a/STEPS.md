# 3/a — POST, create an item, step by step

1. **Describe the JSON shape as a class:**

   ```python
   class Item(BaseModel):
       name: str
       price: float
   ```

   Both fields have no default value, so both are required — send a
   request missing either one and FastAPI rejects it before your
   function ever runs.

2. **Use the class as the route's parameter type:**

   ```python
   @app.post("/items")
   def create_item(item: Item):
       return item
   ```

   Because `Item` isn't a simple type like `int`/`str`, and isn't part
   of the URL, FastAPI knows to read it from the JSON request body.

3. **`item` is a real object**, not a plain dict — `item.name` and
   `item.price` both work, and returning it directly serializes it back
   to JSON automatically.

4. **Try sending bad data** — omit `price`, or send a string where a
   number is expected — and compare the `422` response to what you'd
   have to write by hand to catch the same mistakes.
