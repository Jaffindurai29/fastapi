from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()


@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return [{"id": row.id, "value": row.value} for row in crud.get_items(db)]


@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row.id, "value": row.value}
