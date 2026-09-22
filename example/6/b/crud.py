from sqlalchemy.orm import Session

from models import ItemModel
from schemas import ItemRequest


def create_item(db: Session, item: ItemRequest) -> ItemModel:
    row = ItemModel(value=item.value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def seed_items(db: Session) -> None:
    if db.query(ItemModel).count() == 0:
        db.add_all([ItemModel(value="first"), ItemModel(value="second")])
        db.commit()
