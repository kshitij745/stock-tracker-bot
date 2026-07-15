from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.database.database import SessionLocal
from app.models.product import Product
from app.telegram.states import UPDATE_AFFILIATE


async def affiliate_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    product_id: int,
):
    # Save product id in user session
    context.user_data["affiliate_product_id"] = product_id

    await update.callback_query.message.reply_text(
        "🔗 Send me the Affiliate URL for this product.\n\n"
        "Type /cancel to cancel."
    )

    return UPDATE_AFFILIATE


async def save_affiliate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    product_id = context.user_data.get("affiliate_product_id")

    print(f"DEBUG Product ID : {product_id}")

    if product_id is None:

        await update.message.reply_text(
            "❌ Product ID not found."
        )

        return ConversationHandler.END

    db = SessionLocal()

    try:

        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if product is None:

            await update.message.reply_text(
                "❌ Product not found."
            )

            return ConversationHandler.END

        affiliate = update.message.text.strip()

        print(f"DEBUG Affiliate URL : {affiliate}")

        product.affiliate_url = affiliate

        db.commit()
        db.refresh(product)

        print(f"DEBUG Saved URL : {product.affiliate_url}")

        await update.message.reply_text(
            "✅ Affiliate URL Updated Successfully."
        )

    except Exception as e:

        db.rollback()

        print("Affiliate Save Error:", e)

        await update.message.reply_text(
            f"❌ Error: {e}"
        )

    finally:
        db.close()

    return ConversationHandler.END