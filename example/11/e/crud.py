from sqlalchemy import func
from sqlalchemy.orm import Session

from models import SoftItemModel
from schemas import ItemCreate


def get_items(db: Session, include_deleted: bool = False) -> list[SoftItemModel]:
    query = db.query(SoftItemModel)
    if not include_deleted:
        # The price of soft delete: EVERY normal query needs this filter.
        # Forget it once and "deleted" rows show up again.
        query = query.filter(SoftItemModel.deleted_at.is_(None))
    return query.order_by(SoftItemModel.id).all()


def get_item(db: Session, item_id: int) -> SoftItemModel | None:
    """Any row, deleted or not. Used by restore and permanent delete."""
    return db.get(SoftItemModel, item_id)


def get_live_item(db: Session, item_id: int) -> SoftItemModel | None:
    """Only a row that isn't soft-deleted. What normal reads use."""
    return (
        db.query(SoftItemModel)
        .filter(SoftItemModel.id == item_id, SoftItemModel.deleted_at.is_(None))
        .first()
    )


def create_item(db: Session, item: ItemCreate) -> SoftItemModel:
    row = SoftItemModel(**item.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def soft_delete_item(db: Session, row: SoftItemModel) -> None:
    # An UPDATE, not a DELETE. func.now() lets the database fill in the
    # time, same as server_default in 8/d.
    row.deleted_at = func.now()
    db.commit()


def restore_item(db: Session, row: SoftItemModel) -> SoftItemModel:
    row.deleted_at = None
    db.commit()
    db.refresh(row)
    return row


def hard_delete_item(db: Session, row: SoftItemModel) -> None:
    # A real DELETE. The row is gone and can't be restored.
    db.delete(row)
    db.commit()


def seed(db: Session) -> None:
    if db.query(SoftItemModel).count() == 0:
        db.add_all(
            [
                SoftItemModel(name="Laptop", price=999.99),
                SoftItemModel(name="Mouse", price=19.99),
                SoftItemModel(name="Desk", price=120.0),
            ]
        )
        db.commit()
