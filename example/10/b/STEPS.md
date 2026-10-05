# 10/b — Dependency injection, step by step

Starts from [10/a](../a/STEPS.md). `models.py`, `schemas.py`, `crud.py`,
`main.py` and the router layout are unchanged. What's new is
`dependencies.py`, and how much shorter `routers/items.py` gets because
of it.

A **dependency** is any function (or class) you hand to `Depends(...)`.
Before a route runs, FastAPI calls each of its dependencies, filling in
*their* parameters from the request (path, query, headers, body, or
other dependencies) exactly the way it fills in a route's. Whatever the
dependency returns becomes the route's argument. If it raises
`HTTPException`, the route never runs.

1. **`get_db` — the one you've used since topic 6, now explained.**
   It moved from `database.py` into `dependencies.py`:

   ```python
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

   Because it uses `yield` instead of `return`, it runs in two halves:
   - **before the route:** open a session, then `yield` it. The yielded
     value is what the route gets as `db`.
   - **after the response is ready:** execution resumes after `yield`,
     and `finally` closes the session. `finally` runs even if the route
     raised an exception, so a `404` never leaks a connection.

   Without this, every route would need its own `try`/`finally`.

2. **`get_item_or_404` — a dependency that depends on another one:**

   ```python
   def get_item_or_404(item_id: int, db: Session = Depends(get_db)) -> ItemModel:
       row = crud.get_item(db, item_id)
       if row is None:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found")
       return row
   ```

   `item_id` matches `{item_id}` in the route path, so FastAPI reads it
   (and validates it as an `int`) from the URL. `db` comes from `get_db`.
   FastAPI walks this chain for you: `route → get_item_or_404 → get_db`.

   In [10/a](../a/routers/items.py) every route called the helper by
   hand. Now the routes just *ask for a row*:

   ```python
   # No 404 code here any more: if this function runs, `row` exists.
   @router.get("/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
   def get_item(row: ItemModel = Depends(get_item_or_404)):
       return row
   ```

   ```python
   @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND, dependencies=LOCKED)
   def delete_item(row: ItemModel = Depends(get_item_or_404), db: Session = Depends(get_db)):
       crud.delete_item(db, row)
   ```

   There's no `item_id` parameter on these routes at all. It's still in
   the URL, and still in `/docs`, because the dependency declares it.

3. **One `get_db` call per request, even when it's asked for twice.**
   `DELETE` (and `PATCH`) ask for `get_db` directly *and* through
   `get_item_or_404`. FastAPI caches each dependency's result for the
   length of one request: `get_db` runs once, and both places receive
   the **same** session. That matters: the row was loaded in that
   session, so it can be deleted or committed in it. Two different
   sessions would mean two connections, and a row "belonging" to the
   wrong one. (The rare dependency that must run every time can opt out
   with `Depends(fn, use_cache=False)`.)

4. **`Pagination` — a class as a dependency:**

   ```python
   class Pagination:
       def __init__(
           self,
           skip: int = Query(default=0, ge=0, description="Rows to skip"),
           limit: int = Query(default=10, ge=1, le=100, description="Max rows to return"),
       ):
           self.skip = skip
           self.limit = limit
   ```

   FastAPI only needs something *callable*, and a class is callable:
   `Pagination(skip=..., limit=...)` builds an instance. FastAPI reads
   `__init__`'s parameters as query parameters, validates them with the
   `Query(...)` rules (`?limit=500` is a `422`), and passes the instance
   to the route:

   ```python
   @router.get("", response_model=list[ItemOut])
   def list_items(page: Pagination = Depends(Pagination), db: Session = Depends(get_db)):
       return crud.get_items(db, skip=page.skip, limit=page.limit)
   ```

   Any other list route can reuse `Pagination` and get the same names,
   defaults, limits and docs. `limit` has a maximum so nobody can ask
   for a million rows in one request. (`page: Pagination = Depends()`
   with empty parentheses does the same thing, using the type
   annotation; the explicit form is easier to read.)

5. **`require_api_key` — a guard that returns nothing:**

   ```python
   def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
       expected = os.getenv("API_KEY", "dev-api-key")
       # compare_digest takes the same time whether the first or the last
       # character is wrong, so the key can't be guessed by timing replies.
       if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key")
   ```

   `Header()` reads a request header. FastAPI converts the parameter
   name `x_api_key` to `x-api-key` (underscores become hyphens; header
   names are case-insensitive, so `X-API-Key` matches).

   The default is `None` on purpose. With `Header(...)` (required), a
   missing header would be FastAPI's generic `422`, and the client
   would see a validation error instead of "you're not allowed". Making
   it optional lets *our* code answer `401 Unauthorized` for both
   "missing" and "wrong".

   This is the simplest kind of auth: one shared secret. Real per-user
   login (passwords, tokens) builds on exactly this pattern.

6. **Applying the guard only to write routes:**

   ```python
   # Write routes need a valid X-API-Key header. require_api_key returns
   # nothing, so it goes in dependencies=[...] instead of a parameter.
   LOCKED = [Depends(require_api_key)]
   ```

   ```python
   @router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED, dependencies=LOCKED)
   ```

   `dependencies=[...]` on the decorator runs the dependency but throws
   its return value away, which is right for a guard: the route doesn't
   need anything from it, it just must not run without it. It also runs
   **before** the route's own dependencies, so a missing key is a `401`
   even for an item that doesn't exist.

   **Why per-route, not a second router?** The other option was an
   `admin_router = APIRouter(prefix="/items", dependencies=[Depends(require_api_key)])`
   holding POST/PATCH/DELETE. That's the better tool when a *whole
   group* is locked (say, everything under `/admin`). Here it would
   split one resource across two routers with the same prefix, and
   you'd have to check which router a route is on to know whether it's
   protected. With `dependencies=LOCKED` the lock is visible right on
   the line that defines the route. The same `dependencies=` argument
   also works on `APIRouter(...)` (every route on the router) and on
   `FastAPI(...)` (every route in the app).

7. **`.env.example` — one new variable:**

   ```
   API_KEY=dev-api-key
   ```

   `require_api_key` reads it on every request with
   `os.getenv("API_KEY", "dev-api-key")`, so the app still runs with
   zero setup. [10/c](../c/STEPS.md) moves this, and every other
   setting, into one typed `Settings` class.
