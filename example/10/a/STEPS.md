# 10/a — APIRouter, step by step

`database.py` is the same as [6/a](../../6/a/STEPS.md). `models.py` and
`schemas.py` are the `name`/`price`/`quantity` item from
[topic 8](../../8/README.md), with `ItemOut` from
[8/d](../../8/d). What's new is *where the routes live*.

1. **`routers/__init__.py` — an empty file that makes a package.**
   With it, `routers/` is something Python can import from:
   `from routers import items` loads `routers/items.py`.

2. **`routers/items.py` — an `APIRouter` instead of `app`:**

   ```python
   router = APIRouter(prefix="/items", tags=["items"])
   ```

   An `APIRouter` is a "mini app": it collects routes with exactly the
   same decorators (`@router.get`, `@router.post`, ...), but it can't be
   run by itself. It only does something once it's plugged into a real
   `FastAPI()` app.

3. **`prefix` — write `/items` once, not five times:**

   ```python
   # "" + prefix = "/items". (Writing "/" here would give "/items/".)
   @router.get("", response_model=list[ItemOut])
   def list_items(db: Session = Depends(get_db)):
       return crud.get_items(db)


   @router.get("/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
   def get_item(item_id: int, db: Session = Depends(get_db)):
       return get_item_or_404(db, item_id)
   ```

   The decorator path is glued onto the prefix: `""` becomes `/items`,
   `"/{item_id}"` becomes `/items/{item_id}`. Renaming the resource
   later (say, to `/products`) is now a one-line change.

   Use `""`, not `"/"`, for the collection route. `"/"` registers
   `/items/`, and a request to `/items` would then get a `307` redirect
   to the slash version instead of the data.

4. **`tags` — how `/docs` groups routes.** Every route on this router is
   tagged `items`, and every route on `routers/health.py` is tagged
   `health`. Swagger UI (`/docs`) draws one collapsible section per tag.
   Without tags everything lands in a single "default" list, which gets
   hard to read once an API has a few resources.

5. **`main.py` — no routes left at all:**

   ```python
   from routers import health, items

   ...

   app = FastAPI()

   app.include_router(items.router)
   app.include_router(health.router)
   ```

   `include_router` copies every route from the router onto the app,
   applying the router's `prefix` and `tags` on the way.

   **Why `from routers import items` works:** when you run
   `uvicorn main:app` from inside `10/a`, that folder is the current
   directory, and Python searches it for imports. So `routers` (the
   folder), `crud`, `database`, `models` and `schemas` are all found as
   top-level names. Run uvicorn from somewhere else and you'd get
   `ModuleNotFoundError: No module named 'routers'`. That's why every
   README in this repo says `cd example/<topic>/<letter>` first.

6. **The routers import the shared pieces, not `main.py`:**

   ```python
   import crud
   from database import get_db
   from models import ItemModel
   from schemas import ItemCreate, ItemOut, ItemPatch
   ```

   Nothing ever imports `main`. `main.py` imports the routers, the
   routers import `crud`/`database`/`schemas`. Dependencies point one
   way only, so there are no circular imports.

7. **The helpers moved with the routes.** `get_item_or_404` and
   `ensure_name_free` are only used by item routes, so they live in
   `routers/items.py` beside them:

   ```python
   def get_item_or_404(db: Session, item_id: int) -> ItemModel:
       row = crud.get_item(db, item_id)
       if row is None:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found")
       return row
   ```

   GET, PATCH and DELETE each still have to call it by hand.
   [10/b](../b/STEPS.md) turns it into a dependency so they don't.

8. **`routers/health.py` — a second router, with no prefix:**

   ```python
   router = APIRouter(tags=["health"])


   @router.get("/health")
   def health(db: Session = Depends(get_db)):
       try:
           # The cheapest query there is. If it works, the database is up
           # and the connection settings are right.
           db.execute(text("SELECT 1"))
       except SQLAlchemyError:
           # 503 Service Unavailable — the app is running, but can't do its job.
           return JSONResponse(status_code=503, content={"status": "error", "database": "unreachable"})
       return {"status": "ok", "database": "ok"}
   ```

   A health check is what a load balancer, Docker, or Kubernetes calls
   every few seconds to ask "is this app usable?". Answering `200`
   just because Python is running isn't enough; `SELECT 1` proves the
   database connection works too. `text(...)` marks a raw SQL string
   for SQLAlchemy.

9. **`PATCH` merges, it doesn't replace.** Same as [8/b](../../8/b):
   `model_dump(exclude_unset=True)` keeps only the fields the client
   sent, so `{"price": 899}` leaves `name` and `quantity` alone.
