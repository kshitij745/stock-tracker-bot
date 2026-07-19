import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from app.database.database import SessionLocal
from app.models.product import Product
from app.scheduler.scheduler import executor
from app.services.product_service import check_product


def _run_manual_stock_check(product_id: int):
    """
    Manual Telegram check ko scheduler ke persistent worker par chalata hai.
    Database session bhi isi worker thread ke andar create hoti hai.
    """

    db = SessionLocal()

    try:
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return None

        product, current_status = check_product(
            db=db,
            product=product,
            return_status=True,
        )

        return {
            "product_name": product.product_name,
            "store_name": product.store_name,
            "affiliate_url": product.affiliate_url,
            "current_status": current_status,
        }

    finally:
        db.close()


async def check_stock_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    product_id: int,
):
    await update.callback_query.edit_message_text(
        "⏳ Checking Stock..."
    )

    try:
        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(
            executor,
            _run_manual_stock_check,
            product_id,
        )

        if result is None:
            await update.callback_query.edit_message_text(
                "❌ Product not found."
            )
            return

        current_status = result["current_status"]

        if current_status is True:
            stock_text = "✅ In Stock"

        elif current_status is False:
            stock_text = "❌ Out Of Stock"

        else:
            stock_text = "⚠️ Unable to Determine"

        affiliate = (
            result["affiliate_url"]
            if result["affiliate_url"]
            else "Not Added"
        )

        await update.callback_query.edit_message_text(
            f"📱 <b>{result['product_name']}</b>\n\n"
            f"🏪 Store : {result['store_name']}\n"
            f"📦 Status : {stock_text}\n\n"
            f"🔗 Affiliate :\n{affiliate}",
            parse_mode="HTML",
        )

    except Exception as error:
        await update.callback_query.edit_message_text(
            f"❌ Error\n\n{error}"
        )
