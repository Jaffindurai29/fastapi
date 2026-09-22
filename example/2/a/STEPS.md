# 2/a — Basic path parameter, step by step

1. **Add `{item_id}` inside the path string**: `@app.get("/items/{item_id}")`.
   The curly braces mark a piece of the URL that can change.

2. **Give the function a parameter with the same name**:

   ```python
   def read_item(item_id: int):
       return {"item_id": item_id}
   ```

   `item_id: int` isn't just a hint for you — FastAPI reads it and
   converts the URL text into a real Python `int` before your function
   ever runs. Visit `/items/5` and `item_id` really is the number `5`,
   not the string `"5"`.

3. **See validation happen for free.** Visit `/items/foo` (not a
   number) — FastAPI rejects it with a `422` error before your function
   runs at all. You didn't write any `if` statement for that.
