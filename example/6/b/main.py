from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemRequest

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemRequest, db: Session = Depends(get_db)):
    row = crud.create_item(db, item)
    return {"id": row.id, "value": row.value}
