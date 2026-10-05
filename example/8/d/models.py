from sqlalchemy import Column, DateTime, Float, Integer, String, func

from database import Base


class ItemModel(Base):
    __tablename__ = "response_model_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    # Internal: what we paid the supplier. Must never reach the client.
    supplier_cost = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
