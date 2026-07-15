from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.handlers.delete import (
    delete_product,
    confirm_delete,
    cancel_delete,
)

from app.telegram.handlers.check_stock import (
    check_stock_handler,
)

from app.telegram.keyboards import (
    edit_product_keyboard,
)


async def handle_product_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    action: str,
    product_id: int,
):
    query = update.callback_query

    if action == "delete":
        await delete_product(
            update,
            context,
            product_id,
        )

    elif action == "delete_confirm":
        await confirm_delete(
            update,
            context,
            product_id,
        )

    elif action == "delete_cancel":
        await cancel_delete(
            update,
            context,
        )

    elif action == "check":
        await check_stock_handler(
            update,
            context,
            product_id,
        )

    elif action == "affiliate":
        context.user_data["mode"] = "affiliate"
        context.user_data["product_id"] = product_id

        await query.message.reply_text(
            "🔗 Send the Affiliate URL for this product.\n\n"
            "Type /cancel to cancel."
        )

    elif action == "edit":
        await query.message.reply_text(
            "✏ <b>What do you want to edit?</b>",
            parse_mode="HTML",
            reply_markup=edit_product_keyboard(product_id),
        )


async def handle_edit_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    action: str,
    product_id: int,
):
    query = update.callback_query

    context.user_data["product_id"] = product_id

    if action == "name":
        context.user_data["mode"] = "edit_name"

        await query.message.reply_text(
            "📝 Send the new Product Name."
        )

    elif action == "store":
        context.user_data["mode"] = "edit_store"

        await query.message.reply_text(
            "🏪 Send the new Store Name."
        )

    elif action == "url":
        context.user_data["mode"] = "edit_url"

        await query.message.reply_text(
            "🔗 Send the new Product URL."
        )

    elif action == "affiliate":
        context.user_data["mode"] = "edit_affiliate"

        await query.message.reply_text(
            "💰 Send the new Affiliate URL."
        )

    elif action == "cancel":
        context.user_data.clear()

        await query.message.reply_text(
            "❌ Edit Cancelled."
        )