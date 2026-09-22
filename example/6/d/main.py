from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemPatch

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()


@app.patch("/items/{item_id}")
def update_item(item_id: int, patch: ItemPatch, db: Session = Depends(get_db)):
    row = crud.update_item(db, item_id, patch)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row.id, "value": row.value}
