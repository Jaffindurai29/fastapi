from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
def list_items(include_deleted: bool = False, db: Session = Depends(get_db)):
    return crud.get_items(db, include_deleted)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    # A soft-deleted item answers 404, exactly like a missing one. To
    # the client it IS deleted; only restore can bring it back.
    row = crud.get_live_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_live_item(db, item_id)
    if row is None:  # missing, or already soft-deleted
        raise HTTPException(status_code=404, detail="Item not found")
    crud.soft_delete_item(db, row)


@router.post("/{item_id}/restore", response_model=ItemOut)
def restore_item(item_id: int, db: Session = Depends(get_db)):
    row = crud.get_item(db, item_id)  # deleted rows included on purpose
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if row.deleted_at is None:
        raise HTTPException(status_code=409, detail="Item is not deleted")
    return crud.restore_item(db, row)


@router.delete("/{item_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_permanently(item_id: int, db: Session = Depends(get_db)):
    # Works on live and soft-deleted rows alike (e.g. purging the bin).
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    crud.hard_delete_item(db, row)
