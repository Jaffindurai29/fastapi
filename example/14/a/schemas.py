from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ids import PublicId

Role = Literal["customer", "admin"]
OrderStatus = Literal["pending", "shipped", "delivered", "cancelled"]


# ------------------------------------------------------------- auth ----

# No "role" field: whatever the client sends, sign-ups are customers.
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


# No password, no hash: response_model drops hashed_password even though
# the routes return the full row.
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PublicId
    username: str
    role: Role


class RoleUpdate(BaseModel):
    role: Role


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# --------------------------------------------------------- products ----

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)


# Every field optional: send only what you want to change. No "stock":
# stock only moves through PATCH /products/{id}/stock.
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    is_active: bool | None = None


class StockChange(BaseModel):
    # +10 = 10 arrived, -3 = 3 broke. Not 0: that would do nothing.
    change: int = Field(ne=0)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PublicId
    name: str
    description: str
    price: Decimal
    stock: int
    is_active: bool


# ----------------------------------------------------------- orders ----

class OrderItemIn(BaseModel):
    product_id: str  # the public id, as GET /products showed it
    quantity: int = Field(ge=1, le=100)


class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1)
    phone: str = Field(min_length=5, max_length=30)
    address: str = Field(min_length=5, max_length=300)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: PublicId
    product_name: str
    quantity: int
    unit_price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PublicId
    username: str
    status: OrderStatus
    total: Decimal
    # Decrypted by OrderModel's properties. In MySQL they're ciphertext.
    phone: str
    address: str
    created_at: datetime
    items: list[OrderItemOut]


class StatusUpdate(BaseModel):
    status: OrderStatus
