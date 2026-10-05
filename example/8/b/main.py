from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine, get_db
from schemas import ItemCreate, ItemPatch

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

app = FastAPI()


def to_dict(row):
    return {"id": row.id, "name": row.name, "price": row.price, "quantity": row.quantity}


def get_item_or_404(db: Session, item_id: int):
    row = crud.get_item(db, item_id)
    if row is None:
        # 404 Not Found — the thing the URL points at doesn't exist.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )
    return row


@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return [to_dict(row) for row in crud.get_items(db)]


@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    return to_dict(get_item_or_404(db, item_id))


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    if crud.get_item_by_name(db, item.name) is not None:
        # 409 Conflict — the request is valid, but clashes with data
        # that's already stored.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An item named '{item.name}' already exists",
        )
    return to_dict(crud.create_item(db, item))


@app.patch("/items/{item_id}")
def update_item(item_id: int, patch: ItemPatch, db: Session = Depends(get_db)):
    row = get_item_or_404(db, item_id)

    # exclude_unset=True keeps only the fields the client actually sent.
    changes = patch.model_dump(exclude_unset=True)
    if not changes:
        # 400 Bad Request — well-formed JSON, but it asks for nothing.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Send at least one field to update",
        )
    if None in changes.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fields cannot be set to null",
        )

    new_name = changes.get("name")
    if new_name is not None and new_name != row.name:
        if crud.get_item_by_name(db, new_name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An item named '{new_name}' already exists",
            )

    return to_dict(crud.update_item(db, row, changes))


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    row = get_item_or_404(db, item_id)
    if row.quantity > 0:
        # 409 again — a business rule, not a malformed request.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item {item_id} still has {row.quantity} in stock; set quantity to 0 first",
        )
    crud.delete_item(db, row)
