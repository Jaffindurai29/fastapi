from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from database import Base

# The association (or "join") table. One row = "this item has this tag".
# It has no model class of its own because it holds nothing but the two
# foreign keys. Both columns together form the primary key, so the same
# pair can't be stored twice.
item_tags = Table(
    "rel_item_tags",
    Base.metadata,
    Column("item_id", ForeignKey("rel_items.id"), primary_key=True),
    Column("tag_id", ForeignKey("rel_tags.id"), primary_key=True),
)


# Unchanged from 11/a.
class CategoryModel(Base):
    __tablename__ = "rel_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    items = relationship("ItemModel", back_populates="category")


# Same COLUMNS as 11/a, so the rel_items table is identical and shared.
# The only addition is `tags`, which is a relationship, not a column.
class ItemModel(Base):
    __tablename__ = "rel_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("rel_categories.id"), nullable=False)

    category = relationship("CategoryModel", back_populates="items")
    # secondary= points at the join table. SQLAlchemy reads and writes
    # rel_item_tags for you: item.tags.append(tag) inserts a row there.
    # order_by keeps the list in a stable order in every response.
    tags = relationship(
        "TagModel", secondary=item_tags, back_populates="items", order_by="TagModel.id"
    )


class TagModel(Base):
    __tablename__ = "rel_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True)

    items = relationship(
        "ItemModel", secondary=item_tags, back_populates="tags", order_by="ItemModel.id"
    )
