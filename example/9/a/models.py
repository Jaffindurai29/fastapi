from sqlalchemy import Column, DateTime, Float, Integer, String, func

from database import Base


# 9/a–9/d all use this exact model, so they can share one table.
class ItemModel(Base):
    __tablename__ = "catalog_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
