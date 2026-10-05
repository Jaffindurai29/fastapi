from sqlalchemy.orm import Session

from models import ItemModel
from schemas import ItemCreate


def get_items(db: Session) -> list[ItemModel]:
    return db.query(ItemModel).order_by(ItemModel.id).all()


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def get_item_by_name(db: Session, name: str) -> ItemModel | None:
    return db.query(ItemModel).filter(ItemModel.name == name).first()


def create_item(db: Session, item: ItemCreate) -> ItemModel:
    row = ItemModel(name=item.name, price=item.price, quantity=item.quantity)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_item(db: Session, row: ItemModel, changes: dict) -> ItemModel:
    for field, value in changes.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


def delete_item(db: Session, row: ItemModel) -> None:
    db.delete(row)
    db.commit()


def seed_items(db: Session) -> None:
    if db.query(ItemModel).count() == 0:
        db.add_all(
            [
                ItemModel(name="Laptop", price=999.99, quantity=5),
                ItemModel(name="Mouse", price=19.99, quantity=50),
            ]
        )
        db.commit()
