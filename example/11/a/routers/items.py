from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return crud.get_items(db)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    # Check the foreign key ourselves. MySQL (InnoDB) would reject a bad
    # category_id anyway, but only as an IntegrityError, i.e. a 500.
    # SQLite doesn't enforce foreign keys by default and would happily
    # store it. Checking in code gives a clear 404 on both.
    if crud.get_category(db, item.category_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Category {item.category_id} not found",
        )
    return crud.create_item(db, item)
