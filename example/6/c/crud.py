from sqlalchemy.orm import Session

from models import ItemModel
from schemas import ItemRequest


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def replace_item(db: Session, item_id: int, item: ItemRequest) -> ItemModel | None:
    row = get_item(db, item_id)
    if row is None:
        return None
    row.value = item.value
    db.commit()
    db.refresh(row)
    return row


def seed_items(db: Session) -> None:
    if db.query(ItemModel).count() == 0:
        db.add_all([ItemModel(value="first"), ItemModel(value="second")])
        db.commit()
