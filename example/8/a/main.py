from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemCreate

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()


def to_dict(row):
    return {"id": row.id, "name": row.name, "price": row.price, "quantity": row.quantity}


@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return [to_dict(row) for row in crud.get_items(db)]


# item_id: int is validation too — /items/abc never reaches this function,
# FastAPI answers 422 on its own.
@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return to_dict(row)


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return to_dict(crud.create_item(db, item))
