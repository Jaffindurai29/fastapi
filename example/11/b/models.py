from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


# The "one" side: one category has many items.
class CategoryModel(Base):
    __tablename__ = "rel_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    # Not a column. A Python-side shortcut: category.items runs
    # "SELECT * FROM rel_items WHERE category_id = <this id>" for you.
    items = relationship("ItemModel", back_populates="category")


# The "many" side: every item belongs to exactly one category.
class ItemModel(Base):
    __tablename__ = "rel_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    # The real column. ForeignKey tells the database "this must match an
    # id in rel_categories". nullable=False: no item without a category.
    category_id = Column(Integer, ForeignKey("rel_categories.id"), nullable=False)

    # The other end of CategoryModel.items. back_populates links the two,
    # so setting item.category also appends the item to category.items.
    category = relationship("CategoryModel", back_populates="items")
