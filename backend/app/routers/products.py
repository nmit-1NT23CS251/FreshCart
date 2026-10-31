"""Browse products and check availability. Adding/editing products is admin-only."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_admin
from ..database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_or_404(db: Session, product_id: int) -> models.Product:
    product = db.get(models.Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("", response_model=list[schemas.ProductOut])
def list_products(
    category: str | None = None,
    search: str | None = None,
    in_stock_only: bool = False,
    db: Session = Depends(get_db),
):
    query = select(models.Product)
    if category:
        query = query.where(models.Product.category == category)
    if search and search.strip():
        query = query.where(models.Product.name.ilike(f"%{search.strip()}%"))
    if in_stock_only:
        query = query.where(models.Product.stock > 0)
    return db.scalars(query.order_by(models.Product.category, models.Product.name)).all()


@router.get("/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(
        select(models.Product.category).distinct().order_by(models.Product.category)
    ).all()


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(db, product_id)


@router.get("/{product_id}/availability", response_model=schemas.AvailabilityOut)
def check_availability(
    product_id: int,
    quantity: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    product = get_product_or_404(db, product_id)
    available = product.stock >= quantity
    if product.stock == 0:
        message = f"{product.name} is out of stock"
    elif available:
        message = f"{quantity} x {product.name} available"
    else:
        message = f"Only {product.stock} {product.name} left"
    return schemas.AvailabilityOut(
        product_id=product.id, name=product.name, stock=product.stock,
        requested=quantity, available=available, message=message,
    )


# ---------- Admin only ----------
@router.post("", response_model=schemas.ProductOut, status_code=201)
def create_product(
    data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    product = models.Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    product = get_product_or_404(db, product_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}/stock", response_model=schemas.ProductOut)
def update_stock(
    product_id: int,
    data: schemas.StockUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    product = get_product_or_404(db, product_id)
    product.stock = data.stock
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    product = get_product_or_404(db, product_id)
    db.execute(delete(models.CartItem).where(models.CartItem.product_id == product_id))
    db.delete(product)
    db.commit()
