"""Place an order from the cart with a delivery slot, view your orders, cancel them."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..slots import is_slot_bookable

router = APIRouter(prefix="/orders", tags=["Orders"])


def restore_stock(db: Session, order: models.Order) -> None:
    for item in order.items:
        db.execute(
            update(models.Product)
            .where(models.Product.id == item.product_id)
            .values(stock=models.Product.stock + item.quantity)
        )


@router.post("", response_model=schemas.OrderOut, status_code=201)
def place_order(
    data: schemas.OrderCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_items = db.scalars(
        select(models.CartItem).where(models.CartItem.user_id == user.id)
    ).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Your cart is empty")
    if not is_slot_bookable(db, data.slot_date, data.slot_time):
        raise HTTPException(status_code=400, detail="That delivery slot is no longer available")

    order = models.Order(
        user_id=user.id, slot_date=data.slot_date, slot_time=data.slot_time,
        address=data.address.strip(), status="PENDING",
    )
    total = 0.0

    # Everything below happens in ONE transaction: either all of it is saved, or none of it.
    for item in cart_items:
        product = item.product
        # Atomic stock update: "reduce stock only WHERE there is enough stock".
        # If two people buy the last item at the same time, only one update succeeds.
        result = db.execute(
            update(models.Product)
            .where(models.Product.id == product.id, models.Product.stock >= item.quantity)
            .values(stock=models.Product.stock - item.quantity)
        )
        if result.rowcount == 0:
            name = product.name
            db.rollback()  # undo every stock change made so far
            raise HTTPException(
                status_code=409,
                detail=f"Not enough stock for {name}. Please update your cart.",
            )
        order.items.append(models.OrderItem(
            product_id=product.id, product_name=product.name,
            quantity=item.quantity, price_at_purchase=product.price,
        ))
        total += product.price * item.quantity

    order.total = round(total, 2)
    db.add(order)
    for item in cart_items:
        db.delete(item)  # empty the cart
    if not user.address:
        user.address = order.address  # remember the address for next time
    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[schemas.OrderOut])
def my_orders(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(models.Order)
        .where(models.Order.user_id == user.id)
        .order_by(models.Order.created_at.desc())
    ).all()


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.get(models.Order, order_id)
    if order is None or (order.user_id != user.id and not user.is_admin):
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/cancel", response_model=schemas.OrderOut)
def cancel_order(
    order_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.get(models.Order, order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "PENDING":
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
    restore_stock(db, order)
    order.status = "CANCELLED"
    db.commit()
    db.refresh(order)
    return order
