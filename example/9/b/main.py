from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemOut

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()

NOT_FOUND = {404: {"description": "Item not found"}}


# Every parameter is optional. "= None" means "not sent", and crud.py
# skips that filter entirely.
@app.get("/items", response_model=list[ItemOut])
def list_items(
    search: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    # Literal = a whitelist. Anything else (e.g. sort_by=password) is a 422
    # before our code runs, so a user string never reaches order_by().
    sort_by: Literal["id", "name", "price", "created_at"] = "id",
    order: Literal["asc", "desc"] = "asc",
    skip: int = 0,
    limit: int = 10,
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


@app.get("/items/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row
