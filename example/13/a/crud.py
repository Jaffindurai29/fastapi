from sqlalchemy.orm import Session

from models import ItemModel
from schemas import ItemCreate


def get_items(db: Session) -> list[ItemModel]:
    return db.query(ItemModel).order_by(ItemModel.id).all()


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def create_item(db: Session, item: ItemCreate) -> ItemModel:
    row = ItemModel(**item.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
