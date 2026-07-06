from apscheduler.schedulers.background import BackgroundScheduler

from app.database.database import SessionLocal
from app.models.product import Product
from app.services.product_service import check_product


scheduler = BackgroundScheduler()


def check_all_products():
    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(Product.is_active == True)
            .all()
        )

        print(f"\nChecking {len(products)} active products...")

        for product in products:
            print(f"Checking: {product.product_name}")
            check_product(db, product)

    except Exception as e:
        print(f"Scheduler Error: {e}")

    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        check_all_products,
        "interval",
        minutes=2,   # Change to 5 if you want
        id="stock_checker",
        replace_existing=True
    )

    scheduler.start()

    print("✅ Scheduler Started")