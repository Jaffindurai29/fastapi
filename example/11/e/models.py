from sqlalchemy import Column, DateTime, Float, Integer, String

from database import Base


class SoftItemModel(Base):
    __tablename__ = "soft_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    # NULL = alive. A timestamp = "deleted at this moment". The row
    # itself stays in the table.
    deleted_at = Column(DateTime, nullable=True, default=None)
