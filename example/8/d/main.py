from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemCreate, ItemOut

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()

# Shown in /docs next to each route that can return it.
NOT_FOUND = {404: {"description": "Item not found"}}


# No more hand-built dicts: return the ORM rows directly and let
# response_model decide which fields go out.
@app.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return crud.get_items(db)


@app.get("/items/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row  # still has supplier_cost — ItemOut filters it out


@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    crud.delete_item(db, row)
