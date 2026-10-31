"""Database tables.

User      - customers and admins
Product   - items in the store, with how many are in stock
CartItem  - one row per (user, product) currently in a user's cart
Order     - a placed order with its delivery slot and status
OrderItem - the products inside an order, with the price at the time of purchase
"""
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(String(300), default=None)
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50), index=True)
    price: Mapped[float]
    unit: Mapped[str] = mapped_column(String(30))  # "1 kg", "500 ml", "pack of 6"
    stock: Mapped[int] = mapped_column(default=0)
    emoji: Mapped[str] = mapped_column(String(10), default="🛒")
    description: Mapped[str | None] = mapped_column(String(300), default=None)


class CartItem(Base):
    __tablename__ = "cart_items"
    # A user can have each product only once in the cart (quantity changes instead)
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(default=1)

    product: Mapped["Product"] = relationship()


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    total: Mapped[float] = mapped_column(default=0)
    # PENDING -> PACKED -> OUT_FOR_DELIVERY -> DELIVERED   (or CANCELLED)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)
    slot_date: Mapped[str] = mapped_column(String(10))  # "2026-11-01"
    slot_time: Mapped[str] = mapped_column(String(20))  # "08:00-10:00"
    address: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    # Copies of name and price, so old orders stay correct even if the product changes later
    product_name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int]
    price_at_purchase: Mapped[float]

    order: Mapped["Order"] = relationship(back_populates="items")
