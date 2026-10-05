from typing import Literal

from sqlalchemy.orm import Session

from models import ItemModel

SORT_COLUMNS = {
    "id": ItemModel.id,
    "name": ItemModel.name,
    "price": ItemModel.price,
    "created_at": ItemModel.created_at,
}


# Same step-by-step query as 9/b. The only change: category is now a
# LIST, so one request can ask for several categories at once.
def get_items(
    db: Session,
    skip: int,
    limit: int,
    search: str | None,
    category: list[str] | None,
    min_price: float | None,
    max_price: float | None,
    sort_by: Literal["id", "name", "price", "created_at"],
    order: Literal["asc", "desc"],
) -> list[ItemModel]:
    query = db.query(ItemModel)

    if search is not None:
        query = query.filter(ItemModel.name.ilike(f"%{search}%"))
    if category:
        # ?category=books&category=toys -> WHERE category IN ('books', 'toys')
        query = query.filter(ItemModel.category.in_(category))
    if min_price is not None:
        query = query.filter(ItemModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ItemModel.price <= max_price)

    column = SORT_COLUMNS[sort_by]
    column = column.desc() if order == "desc" else column.asc()
    query = query.order_by(column, ItemModel.id)

    return query.offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


# 25 rows across 5 categories, so paging and filtering have something to do.
SEED = [
    ("Python Crash Course", "books", 29.99),
    ("Clean Code", "books", 34.5),
    ("The Pragmatic Programmer", "books", 42.0),
    ("Dune", "books", 9.99),
    ("Cooking for Engineers", "books", 18.75),
    ("Laptop", "electronics", 999.99),
    ("Mouse", "electronics", 19.99),
    ("Mechanical Keyboard", "electronics", 89.0),
    ("USB-C Cable", "electronics", 7.49),
    ("27in Monitor", "electronics", 249.0),
    ("Noise-Cancelling Headphones", "electronics", 199.95),
    ("Building Blocks Set", "toys", 49.99),
    ("Rubber Duck", "toys", 3.5),
    ("Remote Control Car", "toys", 64.0),
    ("Jigsaw Puzzle 1000pc", "toys", 15.0),
    ("Plush Bear", "toys", 12.25),
    ("Chef's Knife", "kitchen", 79.0),
    ("Cast Iron Pan", "kitchen", 45.5),
    ("Coffee Grinder", "kitchen", 59.99),
    ("Measuring Cups", "kitchen", 8.99),
    ("Garden Hose", "garden", 27.0),
    ("Pruning Shears", "garden", 22.5),
    ("Tomato Seeds", "garden", 2.99),
    ("Watering Can", "garden", 14.0),
    ("Lawn Mower", "garden", 329.0),
]


def seed_items(db: Session) -> None:
    if db.query(ItemModel).count() == 0:
        db.add_all(
            [ItemModel(name=n, category=c, price=p) for n, c, p in SEED]
        )
        db.commit()
