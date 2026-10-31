"""Pydantic schemas: the shape of data coming IN to the API and going OUT of it."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class ORMModel(BaseModel):
    # Lets Pydantic read data straight from SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)


# ---------- Users / Auth ----------
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=120)
    password: str = Field(min_length=6, max_length=72)
    address: str | None = Field(default=None, max_length=300)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Enter a valid email address")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    address: str | None = Field(default=None, max_length=300)


class UserOut(ORMModel):
    id: int
    name: str
    email: str
    address: str | None
    is_admin: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Products ----------
class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    unit: str = Field(min_length=1, max_length=30)
    stock: int = Field(ge=0)
    emoji: str = Field(default="🛒", max_length=10)
    description: str | None = Field(default=None, max_length=300)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    price: float | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    stock: int | None = Field(default=None, ge=0)
    emoji: str | None = Field(default=None, max_length=10)
    description: str | None = Field(default=None, max_length=300)


class ProductOut(ProductBase, ORMModel):
    id: int

    @computed_field
    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @computed_field
    @property
    def low_stock(self) -> bool:
        return 0 < self.stock <= 5


class StockUpdate(BaseModel):
    stock: int = Field(ge=0)


class AvailabilityOut(BaseModel):
    product_id: int
    name: str
    stock: int
    requested: int
    available: bool
    message: str


# ---------- Cart ----------
class CartAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=50)


class CartQuantity(BaseModel):
    quantity: int = Field(ge=1, le=50)


class CartItemOut(ORMModel):
    product: ProductOut
    quantity: int

    @computed_field
    @property
    def subtotal(self) -> float:
        return round(self.product.price * self.quantity, 2)


class CartOut(BaseModel):
    items: list[CartItemOut]
    total: float
    item_count: int


# ---------- Slots & Orders ----------
class SlotOut(BaseModel):
    date: str
    label: str
    time: str
    available: bool
    remaining: int


class OrderCreate(BaseModel):
    slot_date: str
    slot_time: str
    address: str = Field(min_length=5, max_length=300)


class OrderItemOut(ORMModel):
    product_id: int
    product_name: str
    quantity: int
    price_at_purchase: float


class OrderOut(ORMModel):
    id: int
    total: float
    status: str
    slot_date: str
    slot_time: str
    address: str
    created_at: datetime
    items: list[OrderItemOut]


class AdminOrderOut(OrderOut):
    user: UserOut


OrderStatus = Literal["PENDING", "PACKED", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"]


class StatusUpdate(BaseModel):
    status: OrderStatus
