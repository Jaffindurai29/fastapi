# 4/b — POST, step by step

1. **`def list_items()`** — a plain `GET /items` so you can see the
   array's current state before and after posting to it.

2. **`def create_item(value: str)`** — since `value` isn't a Pydantic
   model or a path parameter, FastAPI treats it as a query parameter,
   so it's read from the URL (`?value=third`) instead of a JSON body.

3. **`data.append(value)`** — adds the new value onto the end of
   the shared array.

4. **`return {"index": len(data) - 1, "value": value}`** — tells
   the caller exactly where the new item landed, so a follow-up
   `GET /items/{index}` (or `PUT`/`PATCH`/`DELETE`) knows which index to
   use.
