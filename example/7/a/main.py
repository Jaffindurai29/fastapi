from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemPatch, ItemRequest

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()

# The React dev server (Vite) runs on a different origin/port than this
# API, so the browser needs explicit permission to read the response.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return [{"id": row.id, "value": row.value} for row in crud.get_items(db)]


@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row.id, "value": row.value}


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemRequest, db: Session = Depends(get_db)):
    row = crud.create_item(db, item)
    return {"id": row.id, "value": row.value}


@app.put("/items/{item_id}")
def replace_item(item_id: int, item: ItemRequest, db: Session = Depends(get_db)):
    row = crud.replace_item(db, item_id, item)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row.id, "value": row.value}


@app.patch("/items/{item_id}")
def update_item(item_id: int, patch: ItemPatch, db: Session = Depends(get_db)):
    row = crud.update_item(db, item_id, patch)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row.id, "value": row.value}


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
