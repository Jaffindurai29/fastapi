from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import FilterParams, ItemOut

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()

NOT_FOUND = {404: {"description": "Item not found"}}


# Same parameters as 9/b, now wrapped in Query(...) to add rules.
# Break a rule and FastAPI answers 422 before this function runs.
# description= shows up next to each parameter in /docs.
@app.get("/items", response_model=list[ItemOut])
def list_items(
    search: str | None = Query(
        None, min_length=2, max_length=50, description="Case-insensitive 'name contains'"
    ),
    # A list type tells FastAPI the parameter may repeat:
    # ?category=books&category=toys -> ["books", "toys"]
    category: list[str] | None = Query(None, description="Repeat to match several categories"),
    min_price: float | None = Query(None, ge=0, description="Lowest price, inclusive"),
    max_price: float | None = Query(None, ge=0, description="Highest price, inclusive"),
    sort_by: Literal["id", "name", "price", "created_at"] = "id",
    order: Literal["asc", "desc"] = "asc",
    skip: int = Query(0, ge=0, description="Rows to skip"),
    # le=100 caps the page size, so nobody can ask for a million rows.
    limit: int = Query(10, ge=1, le=100, description="Rows to return (max 100)"),
    db: Session = Depends(get_db),
):
    return crud.get_items(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
    )


# The same filters, declared once as a Pydantic model. This route must
# come BEFORE /items/{item_id}, or "search-model" would be read as an
# item_id (and fail with 422, since it isn't a number).
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


@app.get("/items/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row
