"""Admin-only: see all orders, move them through statuses, and view store stats."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_admin
from ..database import get_db
from .orders import restore_stock

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])

# Which status an order is allowed to move to next
ALLOWED_NEXT = {
    "PENDING": {"PACKED", "CANCELLED"},
    "PACKED": {"OUT_FOR_DELIVERY", "CANCELLED"},
    "OUT_FOR_DELIVERY": {"DELIVERED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}


@router.get("/orders", response_model=list[schemas.AdminOrderOut])
def all_orders(status: str | None = None, db: Session = Depends(get_db)):
    query = select(models.Order).order_by(models.Order.slot_date, models.Order.slot_time)
    if status:
        query = query.where(models.Order.status == status)
    return db.scalars(query).all()


@router.patch("/orders/{order_id}/status", response_model=schemas.AdminOrderOut)
def change_status(order_id: int, data: schemas.StatusUpdate, db: Session = Depends(get_db)):
    order = db.get(models.Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if data.status not in ALLOWED_NEXT[order.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change an order from {order.status} to {data.status}",
        )
    if data.status == "CANCELLED":
        restore_stock(db, order)
    order.status = data.status
    db.commit()
    db.refresh(order)
    return order


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    counts = dict(
        db.execute(
            select(models.Order.status, func.count(models.Order.id)).group_by(models.Order.status)
        ).all()
    )
    revenue = db.scalar(
        select(func.coalesce(func.sum(models.Order.total), 0)).where(
            models.Order.status != "CANCELLED"
        )
    )
    low_stock = db.scalars(
        select(models.Product).where(models.Product.stock <= 5).order_by(models.Product.stock)
    ).all()
    return {
        "orders_by_status": counts,
        "total_orders": sum(counts.values()),
        "revenue": round(revenue, 2),
        "customers": db.scalar(select(func.count(models.User.id)).where(models.User.is_admin.is_(False))),
        "low_stock": [schemas.ProductOut.model_validate(p) for p in low_stock],
    }
