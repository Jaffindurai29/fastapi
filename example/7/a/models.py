from sqlalchemy import Column, Integer, String

from database import Base


class ItemModel(Base):
    __tablename__ = "crud_react_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String(255), nullable=False)
