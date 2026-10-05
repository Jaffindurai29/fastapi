from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import CategoryOut, CategoryWithItems

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


@router.get("/{category_id}", response_model=CategoryWithItems)
def get_category(category_id: int, db: Session = Depends(get_db)):
    row = crud.get_category_with_items(db, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return row
