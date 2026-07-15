from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.database.database import SessionLocal
from app.models.product import Product
from app.telegram.keyboards import product_buttons
from app.telegram.states import SEARCH_PRODUCT


async def search_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🔍 Product name likho:\n\n"
        "Example: Redmi"
    )

    return SEARCH_PRODUCT


async def search_result(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.message.text.strip()

    if not query:
        await update.message.reply_text(
            "❌ Product name empty nahi ho sakta."
        )
        return SEARCH_PRODUCT

    db = SessionLocal()

    try:
        matching_products = (
            db.query(Product)
            .filter(Product.product_name.ilike(f"%{query}%"))
            .order_by(Product.product_name.asc())
            .limit(20)
            .all()
        )

        if not matching_products:
            await update.message.reply_text(
                f'❌ "{query}" naam ka koi product nahi mila.'
            )
            return ConversationHandler.END

        await update.message.reply_text(
            f"🔍 {len(matching_products)} matching product(s) mile:"
        )

        for index, product in enumerate(matching_products, start=1):
            monitoring_status = (
                "🟢 Active"
                if product.is_active
                else "🔴 Inactive"
            )

            stock_status = (
                "✅ In Stock"
                if product.in_stock
                else "❌ Out of Stock"
            )

            message = (
                f"{index}. <b>{product.product_name}</b>\n"
                f"🏪 Store: {product.store_name}\n"
                f"📦 Stock: {stock_status}\n"
                f"📡 Monitoring: {monitoring_status}\n"
                f"🆔 Product ID: {product.id}"
            )

            await update.message.reply_text(
                message,
                parse_mode="HTML",
                reply_markup=product_buttons(product.id),
            )

        return ConversationHandler.END

    except Exception as error:
        await update.message.reply_text(
            f"❌ Search error: {error}"
        )
        return ConversationHandler.END

    finally:
        db.close()