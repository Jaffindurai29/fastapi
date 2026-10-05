from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from ids import decode_id
from models import ItemModel
from schemas import ItemCreate, ItemOut

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()

NOT_FOUND = {404: {"description": "Item not found"}}


# public id -> row, or 404. An invalid public id and an unknown one get
# the SAME answer, so the client can't tell which it was.
def get_item_or_404(db: Session, public_id: str) -> ItemModel:
    item_id = decode_id(public_id)
    row = crud.get_item(db, item_id) if item_id is not None else None
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row


@app.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return [ItemOut.from_row(row) for row in crud.get_items(db)]


# public_id: str, not int. "/items/1" is now just an unknown string -> 404.
@app.get("/items/{public_id}", response_model=ItemOut, responses=NOT_FOUND)
def get_item(public_id: str, db: Session = Depends(get_db)):
    return ItemOut.from_row(get_item_or_404(db, public_id))


@app.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return ItemOut.from_row(crud.create_item(db, item))


@app.delete("/items/{public_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
def delete_item(public_id: str, db: Session = Depends(get_db)):
    crud.delete_item(db, get_item_or_404(db, public_id))
