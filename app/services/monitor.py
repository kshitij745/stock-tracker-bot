from app.database.database import SessionLocal
from app.models.product import Product
from app.services.stock_checker import check_stock


def monitor_products():
    db = SessionLocal()

    try:
        products = db.query(Product).all()

        print("Total products:", len(products))

        for product in products:
            print("Checking:", product.product_name)

            status = check_stock(product.product_url)

            print("Stock Status:", status)

    finally:
        db.close()