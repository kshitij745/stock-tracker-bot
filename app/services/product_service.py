from datetime import datetime
import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.product import Product
from app.services.notifier import send_telegram_message
from app.services.stock_checker import check_stock

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def check_product(db: Session, product: Product):
    """
    Check stock for a Product object, update the database,
    and send a Telegram notification if the product comes back in stock.
    """

    stock_status = check_stock(product.product_url)

    product.last_checked = datetime.utcnow()

    if stock_status is not None:
        product.in_stock = stock_status

    # Send notification only once while product remains in stock
    if stock_status and product.last_notification is None:
        message = (
            f"🎉 Product is Back in Stock!\n\n"
            f"📱 Product: {product.product_name}\n"
            f"🏪 Store: {product.store_name}\n"
            f"🔗 {product.product_url}"
        )

        send_telegram_message(
            bot_token=BOT_TOKEN,
            chat_id=CHAT_ID,
            store_name=product.store_name,
            message=message
        )

        product.last_notification = datetime.utcnow()

    # Reset notification when product goes out of stock
    elif stock_status is False:
        product.last_notification = None

    db.commit()
    db.refresh(product)

    return product


def check_product_stock(db: Session, product_id: int):
    """
    Check stock using product ID.
    Used by the FastAPI endpoint.
    """

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return None

    return check_product(db, product)