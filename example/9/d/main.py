import math
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemOut, ItemPage

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()

NOT_FOUND = {404: {"description": "Item not found"}}


# page/size instead of skip/limit: clients think in page numbers, the
# database thinks in offsets. crud.py does the conversion.
@app.get("/items", response_model=ItemPage)
def list_items(
    search: str | None = Query(None, min_length=2, max_length=50),
    category: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    sort_by: Literal["id", "name", "price", "created_at"] = "id",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    size: int = Query(10, ge=1, le=100, description="Rows per page (max 100)"),
    db: Session = Depends(get_db),
):
    rows, total = crud.get_items_page(
        db,
        page=page,
        size=size,
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
    )
    # A page past the end isn't an error: items is just [], and total/pages
    # still tell the client where the real data ends.
    return {
        "items": rows,  # ORM rows; ItemPage turns each into an ItemOut
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size),
    }


@app.get("/items/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row
