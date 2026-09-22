from sqlalchemy.orm import Session

from models import ItemModel


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


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
