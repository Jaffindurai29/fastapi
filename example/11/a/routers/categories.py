from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import CategoryCreate, CategoryOut, ItemOut

# Every route below lives under /categories (APIRouter is topic 10).
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    if crud.get_category_by_name(db, category.name) is not None:
        raise HTTPException(status_code=409, detail="Category name already exists")
    return crud.create_category(db, category)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    row = crud.get_category(db, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return row


@router.get("/{category_id}/items", response_model=list[ItemOut])
def list_category_items(category_id: int, db: Session = Depends(get_db)):
    # 404 for a missing category, so the client can tell "no such
    # category" apart from "category exists but is empty" ([]).
    if crud.get_category(db, category_id) is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.get_items_in_category(db, category_id)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    row = crud.get_category(db, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    # Deleting it would leave items pointing at a category that no
    # longer exists. Refuse instead of orphaning them.
    count = crud.count_items_in_category(db, category_id)
    if count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Category still has {count} item(s); move or delete them first",
        )
    crud.delete_category(db, row)
