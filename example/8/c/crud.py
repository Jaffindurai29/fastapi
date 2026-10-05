from sqlalchemy.orm import Session

from exceptions import DuplicateItemName, EmptyUpdate, ItemNotFound, ItemStillInStock
from models import ItemModel
from schemas import ItemCreate, ItemPatch


def get_items(db: Session) -> list[ItemModel]:
    return db.query(ItemModel).order_by(ItemModel.id).all()


def get_item(db: Session, item_id: int) -> ItemModel:
    row = db.get(ItemModel, item_id)
    if row is None:
        raise ItemNotFound(item_id)
    return row


def _ensure_name_free(db: Session, name: str) -> None:
    if db.query(ItemModel).filter(ItemModel.name == name).first() is not None:
        raise DuplicateItemName(name)


def create_item(db: Session, item: ItemCreate) -> ItemModel:
    _ensure_name_free(db, item.name)
    row = ItemModel(name=item.name, price=item.price, quantity=item.quantity)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_item(db: Session, item_id: int, patch: ItemPatch) -> ItemModel:
    row = get_item(db, item_id)
    changes = {k: v for k, v in patch.model_dump(exclude_unset=True).items() if v is not None}
    if not changes:
        raise EmptyUpdate()
    if "name" in changes and changes["name"] != row.name:
        _ensure_name_free(db, changes["name"])
    for field, value in changes.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


def delete_item(db: Session, item_id: int) -> None:
    row = get_item(db, item_id)
    if row.quantity > 0:
        raise ItemStillInStock(item_id, row.quantity)
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
