from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import ItemCreate, ItemOut

# No Base.metadata.create_all() here, and no seeding. The table is created
# (and later changed) by Alembic: run `alembic upgrade head` before
# starting the app. create_all only ever creates MISSING tables; it can't
# add a column to one that already exists. Migrations can, and they're
# versioned, reviewable, and reversible.

app = FastAPI()

NOT_FOUND = {404: {"description": "Item not found"}}


@app.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return crud.get_items(db)


@app.get("/items/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row


@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)
