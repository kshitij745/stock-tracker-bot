from datetime import datetime, timedelta

from app.models.product import Product
from app.models.app_setting import AppSetting


def should_send_notification(
    product: Product,
    settings: AppSetting,
    current_time: datetime,
) -> bool:
    """
    Decide karta hai ki current in-stock product ka
    Telegram notification bhejna chahiye ya nahi.
    """

    # Product ke liye pehla notification
    if product.last_notification is None:
        return True

    # Notify Once mode me repeat message nahi jayega
    if settings.notification_mode == "once":
        return False

    # Repeat mode me valid cooldown hona chahiye
    if settings.notification_mode == "repeat":

        cooldown_seconds = settings.notification_cooldown

        if cooldown_seconds <= 0:
            return False

        next_notification_time = (
            product.last_notification
            + timedelta(seconds=cooldown_seconds)
        )

        return current_time >= next_notification_time

    return False


def build_stock_notification_message(
    product: Product,
    buy_link: str,
    is_repeat: bool = False,
) -> str:
    """
    Stock notification ka Telegram message banata hai.
    """

    if is_repeat:
        heading = "🔔 <b>Stock Reminder!</b>"
    else:
        heading = "🎉 <b>Product is Back in Stock!</b>"

    return (
        f"{heading}\n\n"
        f"📱 <b>Product:</b> {product.product_name}\n"
        f"🏪 <b>Store:</b> {product.store_name}\n\n"
        f"🛒 <b>Buy Now:</b>\n{buy_link}"
    )