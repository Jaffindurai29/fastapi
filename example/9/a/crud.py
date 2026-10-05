from sqlalchemy.orm import Session

from models import ItemModel


def get_items(db: Session, skip: int, limit: int) -> list[ItemModel]:
    # ORDER BY first, THEN skip/limit. Without a fixed order the database
    # may return rows in any order, and pages could overlap or skip rows.
    return (
        db.query(ItemModel)
        .order_by(ItemModel.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


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
