from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
