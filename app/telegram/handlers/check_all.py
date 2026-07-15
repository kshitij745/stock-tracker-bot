import asyncio
import time

from telegram import Update
from telegram.ext import ContextTypes

from app.database.database import SessionLocal
from app.models.product import Product
from app.services.product_service import check_product


def run_all_stock_checks():
    """
    Runs all synchronous Playwright stock checks in a separate thread.
    A new database session is created inside that thread.
    """

    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(Product.is_active == True)
            .all()
        )

        total = len(products)
        in_stock = 0
        out_of_stock = 0

        for product in products:
            checked_product = check_product(db, product)

            if checked_product.in_stock:
                in_stock += 1
            else:
                out_of_stock += 1

        return {
            "total": total,
            "in_stock": in_stock,
            "out_of_stock": out_of_stock,
        }

    finally:
        db.close()


async def check_all_products(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    start_time = time.time()

    progress_message = await update.message.reply_text(
        "⏳ Checking all active products..."
    )

    try:
        # Run synchronous Playwright trackers outside the asyncio event loop
        result = await asyncio.to_thread(run_all_stock_checks)

        elapsed_time = round(time.time() - start_time, 2)

        await progress_message.edit_text(
            "✅ <b>Check Completed</b>\n\n"
            f"📦 <b>Total Products:</b> {result['total']}\n"
            f"✅ <b>In Stock:</b> {result['in_stock']}\n"
            f"❌ <b>Out Of Stock:</b> {result['out_of_stock']}\n\n"
            f"⏱ <b>Time:</b> {elapsed_time} seconds",
            parse_mode="HTML",
        )

    except Exception as error:
        await progress_message.edit_text(
            f"❌ Check All failed.\n\n{error}"
        )