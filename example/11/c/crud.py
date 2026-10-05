from sqlalchemy.orm import Session, selectinload

from models import CategoryModel, ItemModel, TagModel
from schemas import ItemCreate, TagCreate


# --- tags ---------------------------------------------------------------

def get_tags(db: Session) -> list[TagModel]:
    return db.query(TagModel).order_by(TagModel.id).all()


def get_tag(db: Session, tag_id: int) -> TagModel | None:
    return db.get(TagModel, tag_id)


def get_tag_by_name(db: Session, name: str) -> TagModel | None:
    return db.query(TagModel).filter(TagModel.name == name).first()


def get_tags_by_ids(db: Session, tag_ids: list[int]) -> list[TagModel]:
    return db.query(TagModel).filter(TagModel.id.in_(tag_ids)).all()


def create_tag(db: Session, tag: TagCreate) -> TagModel:
    row = TagModel(**tag.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# --- items --------------------------------------------------------------

def get_category(db: Session, category_id: int) -> CategoryModel | None:
    return db.get(CategoryModel, category_id)


def get_items(db: Session) -> list[ItemModel]:
    # selectinload (11/b) so listing N items doesn't cost N extra
    # queries for their tags.
    return (
        db.query(ItemModel)
        .options(selectinload(ItemModel.tags))
        .order_by(ItemModel.id)
        .all()
    )


def get_item(db: Session, item_id: int) -> ItemModel | None:
    return db.get(ItemModel, item_id)


def create_item(db: Session, item: ItemCreate, tags: list[TagModel]) -> ItemModel:
    # tag_ids isn't a column, so leave it out of the constructor and
    # set the relationship instead. On commit SQLAlchemy inserts the item
    # row, then one rel_item_tags row per tag.
    row = ItemModel(**item.model_dump(exclude={"tag_ids"}), tags=tags)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def attach_tag(db: Session, item: ItemModel, tag: TagModel) -> ItemModel:
    if tag not in item.tags:  # already attached -> nothing to do
        item.tags.append(tag)
        db.commit()
        db.refresh(item)
    return item


def detach_tag(db: Session, item: ItemModel, tag: TagModel) -> None:
    # Removes the rel_item_tags row only. The item and the tag both stay.
    item.tags.remove(tag)
    db.commit()


# --- seed ---------------------------------------------------------------

def seed(db: Session) -> None:
    # Same categories/items as 11/a and 11/b (the tables are shared).
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
    # Tags are new in 11/c, so they're seeded separately: the items may
    # already exist from running 11/a first.
    if db.query(TagModel).count() == 0:
        sale = TagModel(name="sale")
        new = TagModel(name="new")
        laptop = db.query(ItemModel).filter(ItemModel.name == "Laptop").first()
        guide = db.query(ItemModel).filter(ItemModel.name == "FastAPI Guide").first()
        db.add_all([sale, new])
        if laptop is not None:
            laptop.tags.extend([sale, new])
        if guide is not None:
            guide.tags.append(new)
        db.commit()
