from sqlalchemy.orm import Session

from models import CategoryModel, ItemModel
from schemas import CategoryCreate, ItemCreate


# --- categories ---------------------------------------------------------

def get_categories(db: Session) -> list[CategoryModel]:
    return db.query(CategoryModel).order_by(CategoryModel.id).all()


def get_category(db: Session, category_id: int) -> CategoryModel | None:
    return db.get(CategoryModel, category_id)


def get_category_by_name(db: Session, name: str) -> CategoryModel | None:
    return db.query(CategoryModel).filter(CategoryModel.name == name).first()


def create_category(db: Session, category: CategoryCreate) -> CategoryModel:
    row = CategoryModel(**category.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def count_items_in_category(db: Session, category_id: int) -> int:
    return db.query(ItemModel).filter(ItemModel.category_id == category_id).count()


def delete_category(db: Session, row: CategoryModel) -> None:
    db.delete(row)
    db.commit()


# --- items --------------------------------------------------------------

def get_items(db: Session) -> list[ItemModel]:
    return db.query(ItemModel).order_by(ItemModel.id).all()


def get_items_in_category(db: Session, category_id: int) -> list[ItemModel]:
    return (
        db.query(ItemModel)
        .filter(ItemModel.category_id == category_id)
        .order_by(ItemModel.id)
        .all()
    )


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def create_item(db: Session, item: ItemCreate) -> ItemModel:
    row = ItemModel(**item.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# --- seed ---------------------------------------------------------------

def seed(db: Session) -> None:
    if db.query(CategoryModel).count() == 0:
        electronics = CategoryModel(name="Electronics")
        books = CategoryModel(name="Books")
        # Setting the relationship (category=...) instead of category_id:
        # SQLAlchemy inserts the category first, then fills in the id.
        db.add_all(
            [
                ItemModel(name="Laptop", price=999.99, category=electronics),
                ItemModel(name="Mouse", price=19.99, category=electronics),
                ItemModel(name="FastAPI Guide", price=39.0, category=books),
                ItemModel(name="SQL Basics", price=25.5, category=books),
            ]
        )
        db.commit()
