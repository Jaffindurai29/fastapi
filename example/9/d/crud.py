from typing import Literal

from sqlalchemy.orm import Session

from models import ItemModel

SORT_COLUMNS = {
    "id": ItemModel.id,
    "name": ItemModel.name,
    "price": ItemModel.price,
    "created_at": ItemModel.created_at,
}


def get_items_page(
    db: Session,
    page: int,
    size: int,
    search: str | None,
    category: str | None,
    min_price: float | None,
    max_price: float | None,
    sort_by: Literal["id", "name", "price", "created_at"],
    order: Literal["asc", "desc"],
) -> tuple[list[ItemModel], int]:
    # 1. Build the filtered query, exactly as in 9/b.
    query = db.query(ItemModel)
    if search is not None:
        query = query.filter(ItemModel.name.ilike(f"%{search}%"))
    if category is not None:
        query = query.filter(ItemModel.category == category)
    if min_price is not None:
        query = query.filter(ItemModel.price >= min_price)
    if max_price is not None:
        query = query.filter(ItemModel.price <= max_price)

    # 2. Count it NOW: same filters, but before offset/limit. Counting
    #    db.query(ItemModel) instead would give 25 even when the filter
    #    only matches 5, and the page numbers would be wrong.
    total = query.count()

    # 3. Then sort and cut out one page. page 1 -> rows 0..size-1,
    #    page 2 -> rows size..2*size-1, and so on.
    column = SORT_COLUMNS[sort_by]
    column = column.desc() if order == "desc" else column.asc()
    offset = (page - 1) * size
    rows = query.order_by(column, ItemModel.id).offset(offset).limit(size).all()

    return rows, total


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
