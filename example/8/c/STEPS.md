# 8/c — Custom exception handlers, step by step

Same `database.py`/`models.py`/`schemas.py` as [8/b](../b/STEPS.md).
What changes is *where* errors are decided: `crud.py` raises business
errors, and `main.py` turns them into HTTP responses in one place.

1. **`exceptions.py` — errors in business terms.** One base class
   carries the HTTP status and a machine-readable `code`. Each subclass
   only fills in its message:

   ```python
   class AppError(Exception):
       status_code = 400
       code = "bad_request"

       def __init__(self, message: str):
           super().__init__(message)
           self.message = message


   class ItemNotFound(AppError):
       status_code = 404
       code = "item_not_found"

       def __init__(self, item_id: int):
           super().__init__(f"Item {item_id} not found")
   ```

   `code` is for programs: a frontend can `switch` on it. `message` is
   for humans.

2. **`crud.py` raises instead of returning `None`.** In topic 6,
   `get_item` returned `None` and every route had to check for it. Now:

   ```python
   def get_item(db: Session, item_id: int) -> ItemModel:
       row = db.get(ItemModel, item_id)
       if row is None:
           raise ItemNotFound(item_id)
       return row
   ```

   `crud.py` still knows nothing about HTTP. It never imports
   `HTTPException` or mentions a status code.

3. **One helper builds every error body**, so the shape can't drift:

   ```python
   def error_response(status_code: int, code: str, message: str, fields=None):
       body = {"error": {"code": code, "message": message}}
       if fields:
           body["error"]["fields"] = fields
       return JSONResponse(status_code=status_code, content=body)
   ```

4. **Handler 1 — `@app.exception_handler(AppError)`.** Registering the
   **base** class catches every subclass. To add a new error later, you
   write a new subclass in `exceptions.py`. Nothing in `main.py`
   changes.

5. **Handler 2 — `RequestValidationError`** replaces FastAPI's default
   `422` body (`{"detail": [...]}`) with ours. `exc.errors()` is the
   same list you saw in [8/a](../a/STEPS.md). Each `loc`, like
   `["body", "price"]`, is joined into `"body.price"`.

6. **Handler 3 — Starlette's `HTTPException`.** FastAPI's own `404` for
   unknown URLs and `405` for wrong methods are raised by Starlette, the
   framework underneath FastAPI. Registering the Starlette class catches
   both, and also any FastAPI `HTTPException`, which is a subclass of
   it.

7. **Handler 4 — `Exception`, the catch-all.** Any bug becomes a `500`
   with a generic message. The real error is logged with its traceback
   (`exc_info=exc`) for you, but it's never sent to the client. A stack
   trace can leak file paths, SQL and library versions to an attacker.

8. **The routes are now one line each:**

   ```python
   @app.patch("/items/{item_id}")
   def update_item(item_id: int, patch: ItemPatch, db: Session = Depends(get_db)):
       row = crud.update_item(db, item_id, patch)
       return {"id": row.id, "name": row.name, "price": row.price, "quantity": row.quantity}
   ```

   There's no `if row is None` and no `raise HTTPException`. If anything
   goes wrong inside `crud`, the exception travels up and the matching
   handler answers.
