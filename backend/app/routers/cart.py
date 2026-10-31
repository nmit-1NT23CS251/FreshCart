"""The logged-in user's cart. Stock is checked on every change."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/cart", tags=["Cart"])


def build_cart(db: Session, user: models.User) -> schemas.CartOut:
    items = db.scalars(
        select(models.CartItem)
        .where(models.CartItem.user_id == user.id)
        .order_by(models.CartItem.id)
    ).all()
    total = round(sum(i.product.price * i.quantity for i in items), 2)
    return schemas.CartOut(
        items=items, total=total, item_count=sum(i.quantity for i in items)
    )


def check_stock(product: models.Product, quantity: int) -> None:
    if product.stock == 0:
        raise HTTPException(status_code=400, detail=f"{product.name} is out of stock")
    if quantity > product.stock:
        raise HTTPException(
            status_code=400, detail=f"Only {product.stock} {product.name} available"
        )


def find_item(db: Session, user_id: int, product_id: int) -> models.CartItem | None:
    return db.scalar(
        select(models.CartItem).where(
            models.CartItem.user_id == user_id,
            models.CartItem.product_id == product_id,
        )
    )


@router.get("", response_model=schemas.CartOut)
def get_cart(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_cart(db, user)


@router.post("/items", response_model=schemas.CartOut)
def add_to_cart(
    data: schemas.CartAdd,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(models.Product, data.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    item = find_item(db, user.id, product.id)
    new_quantity = (item.quantity if item else 0) + data.quantity
    check_stock(product, new_quantity)
    if item:
        item.quantity = new_quantity
    else:
        db.add(models.CartItem(user_id=user.id, product_id=product.id, quantity=new_quantity))
    db.commit()
    return build_cart(db, user)


@router.put("/items/{product_id}", response_model=schemas.CartOut)
def set_quantity(
    product_id: int,
    data: schemas.CartQuantity,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = find_item(db, user.id, product_id)
    if item is None:
        raise HTTPException(status_code=404, detail="This item is not in your cart")
    check_stock(item.product, data.quantity)
    item.quantity = data.quantity
    db.commit()
    return build_cart(db, user)


@router.delete("/items/{product_id}", response_model=schemas.CartOut)
def remove_item(
    product_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = find_item(db, user.id, product_id)
    if item:
        db.delete(item)
        db.commit()
    return build_cart(db, user)


@router.delete("", response_model=schemas.CartOut)
def clear_cart(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.execute(delete(models.CartItem).where(models.CartItem.user_id == user.id))
    db.commit()
    return build_cart(db, user)
