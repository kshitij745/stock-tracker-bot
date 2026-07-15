from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.keyboards import settings_keyboard


async def settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "⚙️ Settings",
        reply_markup=settings_keyboard(),
    )