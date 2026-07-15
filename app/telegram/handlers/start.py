from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.permissions import is_admin
from app.telegram.keyboards import main_menu


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text(
            "❌ You are not authorized to use this bot."
        )
        return

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}\n\n"
        "📦 <b>Stock Tracker Admin Panel</b>\n\n"
        "Select an option below.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )