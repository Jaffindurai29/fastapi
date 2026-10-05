from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


def get_item_or_404(db: Session, item_id: int):
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row


def get_tag_or_404(db: Session, tag_id: int):
    tag = crud.get_tag(db, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return crud.get_items(db)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return get_item_or_404(db, item_id)


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    if crud.get_category(db, item.category_id) is None:
        raise HTTPException(status_code=404, detail=f"Category {item.category_id} not found")
    # One query for all the tags, then compare: any id we asked for but
    # didn't get back doesn't exist.
    wanted = set(item.tag_ids)  # set() also drops duplicates like [1, 1]
    tags = crud.get_tags_by_ids(db, list(wanted))
    missing = sorted(wanted - {tag.id for tag in tags})
    if missing:
        raise HTTPException(status_code=404, detail=f"Tag(s) not found: {missing}")
    return crud.create_item(db, item, tags)


# PUT because it's idempotent: attaching a tag that's already attached
# changes nothing and still answers 200.
@router.put("/{item_id}/tags/{tag_id}", response_model=ItemOut)
def attach_tag(item_id: int, tag_id: int, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_id)
    tag = get_tag_or_404(db, tag_id)
    return crud.attach_tag(db, item, tag)


@router.delete("/{item_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_tag(item_id: int, tag_id: int, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_id)
    tag = get_tag_or_404(db, tag_id)
    if tag not in item.tags:
        raise HTTPException(status_code=404, detail="Tag is not attached to this item")
    crud.detach_tag(db, item, tag)
