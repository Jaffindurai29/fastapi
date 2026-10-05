from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from database import Base


class ProductModel(Base):
    __tablename__ = "shop_products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)


class OrderModel(Base):
    __tablename__ = "shop_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    total = Column(Float, nullable=False, default=0)

    # order_by keeps lines in the order they were added.
    lines = relationship("OrderLineModel", back_populates="order", order_by="OrderLineModel.id")


# One row per product in an order: "2 x Keyboard at 50.0 each".
class OrderLineModel(Base):
    __tablename__ = "shop_order_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("shop_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("shop_products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    # Copied from the product at order time. If the price changes next
    # week, this order still shows what the customer actually paid.
    unit_price = Column(Float, nullable=False)

    order = relationship("OrderModel", back_populates="lines")
    product = relationship("ProductModel")
