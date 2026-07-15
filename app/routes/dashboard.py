from fastapi import APIRouter, Request, Form, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.product import Product
from app.services.product_service import check_product

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    search: str = Query(default=""),
    store: str = Query(default=""),
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    # Search
    if search.strip():
        query = query.filter(
            Product.product_name.ilike(f"%{search}%")
        )

    # Store Filter
    if store:
        query = query.filter(
            Product.store_name == store
        )

    products = query.order_by(Product.id.desc()).all()

    total_products = db.query(Product).count()

    active_products = db.query(Product).filter(
        Product.is_active == True
    ).count()

    inactive_products = db.query(Product).filter(
        Product.is_active == False
    ).count()

    in_stock = db.query(Product).filter(
        Product.in_stock == True
    ).count()

    out_of_stock = db.query(Product).filter(
        Product.in_stock == False
    ).count()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": products,
            "search": search,
            "store": store,
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": inactive_products,
            "in_stock": in_stock,
            "out_of_stock": out_of_stock
        }
    )


@router.get("/add", response_class=HTMLResponse)
def add_product_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="add_product.html",
        context={}
    )


@router.post("/add")
def save_product(
    product_name: str = Form(...),
    store_name: str = Form(...),
    product_url: str = Form(...),
    affiliate_url: str = Form(""),
    db: Session = Depends(get_db)
):
    product = Product(
        product_name=product_name,
        store_name=store_name,
        product_url=product_url,
        affiliate_url=affiliate_url if affiliate_url.strip() else None,
        is_active=True
    )

    db.add(product)
    db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@router.get("/edit/{product_id}", response_class=HTMLResponse)
def edit_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={
            "product": product
        }
    )


@router.post("/update/{product_id}")
def update_product(
    product_id: int,
    product_name: str = Form(...),
    store_name: str = Form(...),
    product_url: str = Form(...),
    affiliate_url: str = Form(""),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        product.product_name = product_name
        product.store_name = store_name
        product.product_url = product_url
        product.affiliate_url = affiliate_url if affiliate_url.strip() else None

        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@router.get("/toggle/{product_id}")
def toggle_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        product.is_active = not product.is_active
        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@router.get("/check/{product_id}")
def check_now(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        check_product(db, product)

    return RedirectResponse(
        url="/",
        status_code=303
    )


@router.get("/delete/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product:
        db.delete(product)
        db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )
    
    
@router.get("/products/{product_id}/edit", response_class=HTMLResponse)
def edit_product_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return templates.TemplateResponse(
        "edit_product.html",
        {
            "request": request,
            "product": product,
        },
    )
    
    
@router.post("/products/{product_id}/edit")
def update_product(
    product_id: int,
    product_name: str = Form(...),
    store_name: str = Form(...),
    product_url: str = Form(...),
    affiliate_url: str = Form(""),
    is_active: bool = Form(False),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.product_name = product_name
    product.store_name = store_name
    product.product_url = product_url
    product.affiliate_url = affiliate_url

    product.is_active = is_active

    db.commit()

    return RedirectResponse("/", status_code=303)