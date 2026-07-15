from telegram import Update
from telegram.ext import ContextTypes

from app.database.database import SessionLocal
from app.models.product import Product


VALID_STORES = [
    "Amazon",
    "Flipkart",
    "Croma",
    "Reliance Digital",
    "OnePlus Store",
]


async def text_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    mode = context.user_data.get("mode")

    if not mode:
        return

    product_id = context.user_data.get("product_id")

    if not product_id:
        await update.message.reply_text("❌ Product ID not found.")
        context.user_data.clear()
        return

    new_value = update.message.text.strip()

    db = SessionLocal()

    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            await update.message.reply_text("❌ Product not found.")
            return

        if mode == "affiliate":
            product.affiliate_url = new_value
            success_message = "✅ Affiliate URL Updated Successfully."

        elif mode == "edit_name":
            product.product_name = new_value
            success_message = "✅ Product Name Updated Successfully."

        elif mode == "edit_store":
            if new_value not in VALID_STORES:
                await update.message.reply_text(
                    "❌ Invalid Store.\n\nUse one of these:\n"
                    "Amazon\nFlipkart\nCroma\nReliance Digital\nOnePlus Store"
                )
                return

            product.store_name = new_value
            success_message = "✅ Store Updated Successfully."

        elif mode == "edit_url":
            product.product_url = new_value
            success_message = "✅ Product URL Updated Successfully."

        elif mode == "edit_affiliate":
            product.affiliate_url = new_value
            success_message = "✅ Affiliate URL Updated Successfully."

        else:
            return

        db.commit()

        await update.message.reply_text(success_message)

    except Exception as e:
        db.rollback()
        await update.message.reply_text(f"❌ Error: {e}")

    finally:
        db.close()
        context.user_data.clear()