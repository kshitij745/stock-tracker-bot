from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.keyboards import (
    settings_keyboard,
    scheduler_interval_keyboard,
    notification_cooldown_keyboard,
)


async def handle_settings_menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    action: str,
):
    query = update.callback_query

    if action == "interval":
        await query.message.reply_text(
            "🔄 <b>Select Scheduler Interval</b>",
            parse_mode="HTML",
            reply_markup=scheduler_interval_keyboard(),
        )

    elif action == "cooldown":
        await query.message.reply_text(
            "🔔 <b>Notification Settings</b>\n\n"
            "✅ Notify Once\n\n"
            "🔁 Repeat Reminder",
            parse_mode="HTML",
            reply_markup=notification_cooldown_keyboard(),
        )

    elif action == "back":
        await query.message.reply_text(
            "⚙️ <b>Settings</b>",
            parse_mode="HTML",
            reply_markup=settings_keyboard(),
        )