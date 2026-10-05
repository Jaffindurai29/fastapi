from sqlalchemy import Column, Float, Integer, String

from database import Base


class ItemModel(Base):
    __tablename__ = "structured_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
