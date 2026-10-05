from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import ItemSummary, TagCreate, TagOut

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)):
    return crud.get_tags(db)


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    if crud.get_tag_by_name(db, tag.name) is not None:
        raise HTTPException(status_code=409, detail="Tag name already exists")
    return crud.create_tag(db, tag)


@router.get("/{tag_id}/items", response_model=list[ItemSummary])
def list_tag_items(tag_id: int, db: Session = Depends(get_db)):
    tag = crud.get_tag(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    # The other direction of the same join table: tag.items.
    return tag.items
