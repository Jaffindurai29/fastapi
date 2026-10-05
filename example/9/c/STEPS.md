# 9/c — `Query(...)` validation, step by step

Same `database.py` and `models.py` as [9/a](../a/STEPS.md), same
step-by-step query as [9/b](../b/STEPS.md). What's new: rules on every
parameter, a repeatable `category`, and a second way to declare all of
it.

1. **`main.py` — `Query(...)` is `Field(...)` for query parameters.**

   ```python
   skip: int = Query(0, ge=0, description="Rows to skip"),
   # le=100 caps the page size, so nobody can ask for a million rows.
   limit: int = Query(10, ge=1, le=100, description="Rows to return (max 100)"),
   ```

   The first argument is the default, exactly like `= 10` was in 9/b.
   The rest are the same rules you met on body fields in
   [8/a](../../8/a/STEPS.md): `ge`/`le`/`gt`/`lt` for numbers,
   `min_length`/`max_length` for strings. Break one and FastAPI answers
   `422` before the function runs, listing every broken rule at once.

   This closes both holes left by [9/a](../a/STEPS.md): `?limit=1000000`
   is now refused (the response size is bounded again) and so is
   `?skip=-1` (which MySQL would have rejected with a `500`).

2. **`search` needs at least 2 characters.**

   ```python
   search: str | None = Query(
       None, min_length=2, max_length=50, description="Case-insensitive 'name contains'"
   ),
   ```

   A one-letter search matches nearly every row, so it's not a useful
   filter, just an expensive one. `max_length=50` stops someone posting
   a 10 MB search string. The rules only apply when the parameter is
   sent; leaving it out is still fine because the default is `None`.

3. **`description=` shows up in `/docs`.** Every `Query(...)` above
   has one. Open `/docs`, expand `GET /items`, and each parameter has a
   line of help next to it, plus its limits (`maximum: 100`). It costs
   nothing and saves every client developer a question.

4. **A repeatable parameter: `list[str]`.**

   ```python
   # A list type tells FastAPI the parameter may repeat:
   # ?category=books&category=toys -> ["books", "toys"]
   category: list[str] | None = Query(None, description="Repeat to match several categories"),
   ```

   With a plain `str`, FastAPI would keep only the last value (`toys`). With
   `list[str]` it collects all of them. `Query(...)` is required here:
   without it, FastAPI would assume a list argument is a JSON **body**.

   In `crud.py`, the list becomes an `IN` filter:

   ```python
   if category:
       # ?category=books&category=toys -> WHERE category IN ('books', 'toys')
       query = query.filter(ItemModel.category.in_(category))
   ```

   `if category:` (not `is not None`) also skips an empty list, because
   `IN ()` with nothing in it isn't valid SQL on every database.

5. **The same filters as one Pydantic model.** Eight parameters is a
   long function signature, and a second route that wants the same
   filters would have to copy all of them. `schemas.py` gathers them
   into a model instead:

   ```python
   class FilterParams(BaseModel):
       # Unknown query parameters (a typo like ?limt=5) become a 422
       # instead of being silently ignored.
       model_config = {"extra": "forbid"}

       search: str | None = Field(
           None, min_length=2, max_length=50, description="Case-insensitive 'name contains'"
       )
       category: list[str] | None = Field(None, description="Repeat to match several categories")
       min_price: float | None = Field(None, ge=0, description="Lowest price, inclusive")
       max_price: float | None = Field(None, ge=0, description="Highest price, inclusive")
       sort_by: Literal["id", "name", "price", "created_at"] = "id"
       order: Literal["asc", "desc"] = "asc"
       skip: int = Field(0, ge=0, description="Rows to skip")
       limit: int = Field(10, ge=1, le=100, description="Rows to return (max 100)")
   ```

   Same rules, written with `Field(...)` because it's a normal Pydantic
   model. It can be reused by any route, and tested on its own.

6. **`main.py` — telling FastAPI "this model comes from the query".**

   ```python
   @app.get("/items/search-model", response_model=list[ItemOut])
   def search_items(
       # The one place this repo uses Annotated: it's how FastAPI documents
       # query-parameter models. Query() says "fill this model's fields from
       # the query string", not from a JSON body.
       filters: Annotated[FilterParams, Query()],
       db: Session = Depends(get_db),
   ):
       # Field names match crud.get_items' arguments, so ** unpacks them.
       return crud.get_items(db, **filters.model_dump())
   ```

   A Pydantic model argument normally means "JSON body" ([8/a](../../8/a/STEPS.md)).
   `Query()` overrides that: FastAPI reads each field of `FilterParams`
   from the query string instead. This feature arrived in FastAPI
   0.115.

   **Why `Annotated` here, when the rest of the repo writes
   `db: Session = Depends(get_db)`?** `Annotated[Type, Query()]` keeps
   the type and the "where does it come from" marker together, and it's
   the form FastAPI's documentation uses for query-parameter models.
   This is the only place in the repo that uses it; everywhere else
   keeps the default-argument style from earlier topics. (Current
   FastAPI also accepts `filters: FilterParams = Query()`, but stick to
   the documented form for this feature.)

   `/docs` shows the same eight parameters for this route as for
   `GET /items`, because FastAPI unpacks the model's fields one by one.

7. **`extra: forbid` catches typos.** `GET /items?limt=5` is accepted:
   FastAPI only looks for the parameters you declared, and ignores the
   rest. The client gets 10 rows and thinks `limit` is broken.
   `GET /items/search-model?limt=5` is a `422` with type
   `extra_forbidden`, pointing straight at the typo. That's only
   possible with a model, because only a model knows the full list of
   allowed names.

8. **Route order matters.** `/items/search-model` is declared
   **before** `/items/{item_id}`. FastAPI tries routes top to bottom,
   and `{item_id}` would happily match the text `search-model`, then
   fail with `422` because it isn't a number. Fixed paths go before
   path parameters that could swallow them.

9. **What's still missing.** The client gets a page of rows but has no
   idea how many there are in total, so it can't show "Page 2 of 3" or
   know when to stop clicking Next. [9/d](../d/STEPS.md) wraps the page
   in an envelope with `total` and `pages`.
