from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import check_product_stock

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        product_name=product.product_name,
        store_name=product.store_name,
        product_url=product.product_url,
        affiliate_url=product.affiliate_url,
        price=product.price
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    updated_product: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.product_name = updated_product.product_name
    product.store_name = updated_product.store_name
    product.product_url = updated_product.product_url
    product.affiliate_url = updated_product.affiliate_url
    product.price = updated_product.price
    product.in_stock = updated_product.in_stock
    product.is_active = updated_product.is_active

    db.commit()
    db.refresh(product)

    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }


@router.get("/{product_id}/check-stock")
def check_stock(product_id: int, db: Session = Depends(get_db)):
    product = check_product_stock(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "product_id": product.id,
        "product_name": product.product_name,
        "in_stock": product.in_stock,
        "last_checked": product.last_checked,
        "message": "Stock checked successfully"
    }