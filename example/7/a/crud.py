from sqlalchemy.orm import Session

from models import ItemModel
from schemas import ItemPatch, ItemRequest


def get_items(db: Session) -> list[ItemModel]:
    return db.query(ItemModel).order_by(ItemModel.id).all()


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def create_item(db: Session, item: ItemRequest) -> ItemModel:
    row = ItemModel(value=item.value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def replace_item(db: Session, item_id: int, item: ItemRequest) -> ItemModel | None:
    row = get_item(db, item_id)
    if row is None:
        return None
    row.value = item.value
    db.commit()
    db.refresh(row)
    return row


def update_item(db: Session, item_id: int, patch: ItemPatch) -> ItemModel | None:
    row = get_item(db, item_id)
    if row is None:
        return None
    if patch.value is not None:
        row.value = patch.value
    db.commit()
    db.refresh(row)
    return row


def delete_item(db: Session, item_id: int) -> bool:
    row = get_item(db, item_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


def seed_items(db: Session) -> None:
    if db.query(ItemModel).count() == 0:
        db.add_all([ItemModel(value="first"), ItemModel(value="second")])
        db.commit()
