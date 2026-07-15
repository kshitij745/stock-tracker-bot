from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes

from app.database.database import SessionLocal
from app.models.product import Product


async def delete_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    product_id: int,
):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Yes",
                    callback_data=f"product:delete_confirm:{product_id}",
                ),
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data=f"product:delete_cancel:{product_id}",
                ),
            ]
        ]
    )

    await update.callback_query.edit_message_text(
        "⚠️ Are you sure?\n\n"
        "This product will be deleted permanently.",
        reply_markup=keyboard,
    )


async def confirm_delete(
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

    product_name = product.product_name

    db.delete(product)

    db.commit()

    db.close()

    await update.callback_query.edit_message_text(
        f"✅ Product Deleted Successfully\n\n"
        f"📱 {product_name}"
    )


async def cancel_delete(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.callback_query.edit_message_text(
        "❌ Delete Cancelled."
    )