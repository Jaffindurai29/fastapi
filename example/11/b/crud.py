from sqlalchemy.orm import Session, joinedload, selectinload

from models import CategoryModel, ItemModel


# --- categories ---------------------------------------------------------

def get_categories(db: Session) -> list[CategoryModel]:
    return db.query(CategoryModel).order_by(CategoryModel.id).all()


def get_category_with_items(db: Session, category_id: int) -> CategoryModel | None:
    # selectinload: after loading the category, run ONE more query
    # "SELECT ... FROM rel_items WHERE category_id IN (...)" and attach
    # the results to category.items.
    return (
        db.query(CategoryModel)
        .options(selectinload(CategoryModel.items))
        .filter(CategoryModel.id == category_id)
        .first()
    )


# --- items --------------------------------------------------------------

def get_items(db: Session) -> list[ItemModel]:
    # Without .options(...) this would be the N+1 problem: 1 query for
    # the items, then 1 more per item the moment Pydantic reads
    # item.category. selectinload makes it 2 queries total, however
    # many items there are.
    return (
        db.query(ItemModel)
        .options(selectinload(ItemModel.category))
        .order_by(ItemModel.id)
        .all()
    )


def get_item(db: Session, item_id: int) -> ItemModel | None:
    # joinedload: fetch the item AND its category in a single query
    # with a JOIN. Good fit for "one row plus its parent".
    return (
        db.query(ItemModel)
        .options(joinedload(ItemModel.category))
        .filter(ItemModel.id == item_id)
        .first()
    )


# --- seed ---------------------------------------------------------------

# Same tables and same seed data as 11/a, so whichever runs first fills
# them and the other one skips.
def seed(db: Session) -> None:
    if db.query(CategoryModel).count() == 0:
        electronics = CategoryModel(name="Electronics")
        books = CategoryModel(name="Books")
        db.add_all(
            [
                ItemModel(name="Laptop", price=999.99, category=electronics),
                ItemModel(name="Mouse", price=19.99, category=electronics),
                ItemModel(name="FastAPI Guide", price=39.0, category=books),
                ItemModel(name="SQL Basics", price=25.5, category=books),
            ]
        )
        db.commit()
