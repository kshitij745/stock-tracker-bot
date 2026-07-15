import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from app.database.database import SessionLocal
from app.models.product import Product
from app.services.product_service import check_product


async def check_stock_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    product_id: int,
):

    db = SessionLocal()

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:

        db.close()

        await update.callback_query.edit_message_text(
            "❌ Product not found."
        )

        return

    await update.callback_query.edit_message_text(
        "⏳ Checking Stock..."
    )

    try:
        # Run sync Playwright code in a background thread
        product = await asyncio.to_thread(
            check_product,
            db,
            product,
        )

        stock = "✅ In Stock" if product.in_stock else "❌ Out Of Stock"

        affiliate = (
            product.affiliate_url
            if product.affiliate_url
            else "Not Added"
        )

        await update.callback_query.edit_message_text(
            f"📱 <b>{product.product_name}</b>\n\n"
            f"🏪 Store : {product.store_name}\n"
            f"📦 Status : {stock}\n\n"
            f"🔗 Affiliate :\n{affiliate}",
            parse_mode="HTML",
        )

    except Exception as e:

        await update.callback_query.edit_message_text(
            f"❌ Error\n\n{e}"
        )

    finally:
        db.close()