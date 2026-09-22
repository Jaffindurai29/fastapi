from sqlalchemy.orm import Session

from models import ItemModel
from schemas import ItemPatch


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def update_item(db: Session, item_id: int, patch: ItemPatch) -> ItemModel | None:
    row = get_item(db, item_id)
    if row is None:
        return None
    if patch.value is not None:
        row.value = patch.value
    db.commit()
    db.refresh(row)
    return row


def seed_items(db: Session) -> None:
    if db.query(ItemModel).count() == 0:
        db.add_all([ItemModel(value="first"), ItemModel(value="second")])
        db.commit()
