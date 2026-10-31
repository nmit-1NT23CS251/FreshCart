"""Fills an empty database with an admin account and sample products."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .auth import hash_password

ADMIN_EMAIL = "admin@grocery.com"
ADMIN_PASSWORD = "admin123"

# (name, category, price, unit, stock, emoji)
PRODUCTS = [
    ("Toned Milk", "Dairy", 28, "500 ml", 40, "🥛"),
    ("Curd", "Dairy", 35, "400 g", 25, "🥣"),
    ("Paneer", "Dairy", 90, "200 g", 12, "🧀"),
    ("Butter", "Dairy", 58, "100 g", 4, "🧈"),
    ("Eggs", "Dairy", 84, "pack of 12", 20, "🥚"),
    ("Tomato", "Vegetables", 30, "1 kg", 50, "🍅"),
    ("Onion", "Vegetables", 40, "1 kg", 60, "🧅"),
    ("Potato", "Vegetables", 35, "1 kg", 45, "🥔"),
    ("Carrot", "Vegetables", 48, "500 g", 3, "🥕"),
    ("Spinach", "Vegetables", 25, "1 bunch", 0, "🥬"),
    ("Banana", "Fruits", 60, "1 dozen", 30, "🍌"),
    ("Apple", "Fruits", 180, "1 kg", 18, "🍎"),
    ("Orange", "Fruits", 120, "1 kg", 15, "🍊"),
    ("Grapes", "Fruits", 90, "500 g", 0, "🍇"),
    ("Whole Wheat Bread", "Bakery", 45, "400 g", 22, "🍞"),
    ("Croissant", "Bakery", 60, "pack of 2", 5, "🥐"),
    ("Basmati Rice", "Staples", 150, "1 kg", 35, "🍚"),
    ("Wheat Atta", "Staples", 260, "5 kg", 20, "🌾"),
    ("Toor Dal", "Staples", 140, "1 kg", 25, "🫘"),
    ("Sunflower Oil", "Staples", 165, "1 L", 18, "🫗"),
    ("Sugar", "Staples", 48, "1 kg", 30, "🧂"),
    ("Tea Powder", "Beverages", 120, "250 g", 16, "🍵"),
    ("Instant Coffee", "Beverages", 210, "100 g", 10, "☕"),
    ("Orange Juice", "Beverages", 110, "1 L", 8, "🧃"),
    ("Potato Chips", "Snacks", 20, "52 g", 50, "🥔"),
    ("Biscuits", "Snacks", 30, "200 g", 40, "🍪"),
]


def seed_database(db: Session) -> None:
    if db.scalar(select(models.User).where(models.User.email == ADMIN_EMAIL)) is None:
        db.add(models.User(
            name="Store Admin", email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD), is_admin=True,
        ))
    if db.scalar(select(models.Product).limit(1)) is None:
        for name, category, price, unit, stock, emoji in PRODUCTS:
            db.add(models.Product(
                name=name, category=category, price=price,
                unit=unit, stock=stock, emoji=emoji,
            ))
    db.commit()
