from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from dependencies import Pagination, get_db, get_item_or_404, require_api_key
from models import ItemModel
from schemas import ItemCreate, ItemOut, ItemPatch

router = APIRouter(prefix="/items", tags=["items"])

NOT_FOUND = {404: {"description": "Item not found"}}

# Write routes need a valid X-API-Key header. require_api_key returns
# nothing, so it goes in dependencies=[...] instead of a parameter.
LOCKED = [Depends(require_api_key)]


def ensure_name_free(db: Session, name: str) -> None:
    if crud.get_item_by_name(db, name) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An item named '{name}' already exists",
        )


@router.get("", response_model=list[ItemOut])
def list_items(page: Pagination = Depends(Pagination), db: Session = Depends(get_db)):
    return crud.get_items(db, skip=page.skip, limit=page.limit)


# No 404 code here any more: if this function runs, `row` exists.
@router.get("/{item_id}", response_model=ItemOut, responses=NOT_FOUND)
def get_item(row: ItemModel = Depends(get_item_or_404)):
    return row


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED, dependencies=LOCKED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    ensure_name_free(db, item.name)
    return crud.create_item(db, item)


# Both get_item_or_404 and this route ask for get_db. FastAPI calls
# get_db ONCE for this request and hands the same session to both.
@router.patch("/{item_id}", response_model=ItemOut, responses=NOT_FOUND, dependencies=LOCKED)
def update_item(patch: ItemPatch, row: ItemModel = Depends(get_item_or_404), db: Session = Depends(get_db)):
    # exclude_unset=True keeps only the fields the client actually sent.
    changes = patch.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Send at least one field to update")
    if None in changes.values():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fields cannot be set to null")
    if "name" in changes and changes["name"] != row.name:
        ensure_name_free(db, changes["name"])

    return crud.update_item(db, row, changes)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND, dependencies=LOCKED)
def delete_item(row: ItemModel = Depends(get_item_or_404), db: Session = Depends(get_db)):
    crud.delete_item(db, row)
