# 4/a — GET, step by step

1. **Seed the array with two items**, so this example is testable on
   its own: `data = ["first", "second"]`.

2. **`GET /items` returns it as-is** — showing everything.

3. **`GET /items/{item_index}` reaches one entry by its position**, with
   a bounds check before indexing (an out-of-range index would
   otherwise raise Python's own `IndexError` and crash into a generic
   `500`, instead of a clean `404`):

   ```python
   if item_index < 0 or item_index >= len(data):
       raise HTTPException(status_code=404, detail="Item not found")
   ```

This is the read half of CRUD — Create/Update/Delete are the other four
letters in this topic.
