from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from models import ItemModel
from schemas import ItemCreate, ItemOut, ItemPatch

# prefix: every path below starts with /items, so the decorators only
#         write the part after it.
# tags:   groups these routes under an "items" heading in /docs.
router = APIRouter(prefix="/items", tags=["items"])

NOT_FOUND = {404: {"description": "Item not found"}}


def get_item_or_404(db: Session, item_id: int) -> ItemModel:
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found")
    return row


def ensure_name_free(db: Session, name: str) -> None:
    if crud.get_item_by_name(db, name) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An item named '{name}' already exists",
        )


# "" + prefix = "/items". (Writing "/" here would give "/items/".)
@router.get("", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return crud.get_items(db)


@router.get("/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return get_item_or_404(db, item_id)


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    ensure_name_free(db, item.name)
    return crud.create_item(db, item)


@router.patch("/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
def update_item(item_id: int, patch: ItemPatch, db: Session = Depends(get_db)):
    row = get_item_or_404(db, item_id)

    # exclude_unset=True keeps only the fields the client actually sent.
    changes = patch.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Send at least one field to update")
    if None in changes.values():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be set to null")
    if "name" in changes and changes["name"] != row.name:
        ensure_name_free(db, changes["name"])

    return crud.update_item(db, row, changes)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    row = get_item_or_404(db, item_id)
    crud.delete_item(db, row)
