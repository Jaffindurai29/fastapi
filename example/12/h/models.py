from sqlalchemy import Column, Float, Integer, String

from database import Base


class ItemModel(Base):
    __tablename__ = "public_id_items"

    # Still a plain auto-increment integer. Public ids are computed from
    # it on the way out; nothing extra is stored.
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
