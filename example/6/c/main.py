from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemRequest

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()


@app.put("/items/{item_id}")
def replace_item(item_id: int, item: ItemRequest, db: Session = Depends(get_db)):
    row = crud.replace_item(db, item_id, item)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row.id, "value": row.value}
