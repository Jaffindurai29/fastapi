from sqlalchemy.orm import Session

from models import ItemModel
from schemas import ItemCreate


# crud.py only ever deals with real integer ids. Encoding/decoding
# public ids is the route's job (main.py).

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


def delete_item(db: Session, row: ItemModel) -> None:
    db.delete(row)
    db.commit()


def seed_items(db: Session) -> None:
    if db.query(ItemModel).count() == 0:
        db.add_all(
            [
                ItemModel(name="Laptop", price=999.99),
                ItemModel(name="Mouse", price=19.99),
                ItemModel(name="Keyboard", price=49.5),
            ]
        )
        db.commit()
