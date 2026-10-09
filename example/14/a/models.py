from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from database import Base
from encryption import decrypt


class UserModel(Base):
    __tablename__ = "minishop_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=False, unique=True)
    # Only the HASH is stored. There is no "password" column at all.
    hashed_password = Column(String(255), nullable=False)
    # "customer" or "admin". Sign-ups are always customers; only an admin
    # (or create_admin.py) can promote someone.
    role = Column(String(20), nullable=False, default="customer")


class ProductModel(Base):
    __tablename__ = "minishop_products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False, default="")
    # Numeric, not Float: money must not pick up rounding errors.
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    # "Deleting" hides the product instead (soft delete, 11/e), so old
    # orders that point at it still make sense.
    is_active = Column(Boolean, nullable=False, default=True)


class OrderModel(Base):
    __tablename__ = "minishop_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("minishop_users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total = Column(Numeric(10, 2), nullable=False)
    # ENCRYPTED, not hashed: we must read the address again to ship the
    # order. Without FERNET_KEY these columns are unreadable.
    phone_encrypted = Column(Text, nullable=False)
    address_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship(UserModel)
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")

    # Decrypted on the way out. OrderOut reads these properties, never the
    # *_encrypted columns.
    @property
    def phone(self) -> str:
        return decrypt(self.phone_encrypted)

    @property
    def address(self) -> str:
        return decrypt(self.address_encrypted)

    @property
    def username(self) -> str:
        return self.user.username


class OrderItemModel(Base):
    __tablename__ = "minishop_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("minishop_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("minishop_products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    # Copied from the product when the order is placed, so a later price
    # change doesn't rewrite what the customer actually paid.
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship(OrderModel, back_populates="items")
    product = relationship(ProductModel)

    @property
    def product_name(self) -> str:
        return self.product.name
