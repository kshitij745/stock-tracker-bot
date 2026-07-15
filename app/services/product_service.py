from datetime import datetime
import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.product import Product
from app.services.notifier import send_telegram_message
from app.services.stock_checker import check_stock
from app.services.settings_service import get_app_settings
from app.services.notification_service import (
    should_send_notification,
    build_stock_notification_message,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def check_product(db: Session, product: Product):
    """
    Product stock check karta hai, database update karta hai,
    aur notification settings ke hisaab se Telegram message bhejta hai.
    """

    stock_status = check_stock(product.product_url)
    current_time = datetime.utcnow()

    product.last_checked = current_time

    if stock_status is not None:
        product.in_stock = stock_status

    buy_link = (
        product.affiliate_url
        if product.affiliate_url and product.affiliate_url.strip()
        else product.product_url
    )

    settings = get_app_settings(db)

    # Product currently in stock
    if stock_status is True:

        send_notification = should_send_notification(
            product=product,
            settings=settings,
            current_time=current_time,
        )

        if send_notification:

            is_repeat = product.last_notification is not None

            message = build_stock_notification_message(
                product=product,
                buy_link=buy_link,
                is_repeat=is_repeat,
            )

            sent = send_telegram_message(
                bot_token=BOT_TOKEN,
                chat_id=CHAT_ID,
                store_name=product.store_name,
                message=message,
            )

            if sent:
                product.last_notification = current_time

    # Product out of stock hone par notification cycle reset
    elif stock_status is False:
        product.last_notification = None

    db.commit()
    db.refresh(product)

    return product


def check_product_stock(db: Session, product_id: int):
    """
    Product ID se stock check karta hai.
    FastAPI endpoint ke liye use hota hai.
    """

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        return None

    return check_product(db, product)