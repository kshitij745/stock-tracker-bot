from telegram import Update
from telegram.ext import ContextTypes

from app.database.database import SessionLocal
from app.services.settings_service import (
    get_app_settings,
    update_notification_settings,
)
from app.telegram.keyboards import (
    notification_cooldown_keyboard,
    settings_keyboard,
)


def format_cooldown(seconds: int) -> str:
    if seconds == 0:
        return "Notify Once"

    if seconds < 60:
        return f"{seconds} seconds"

    minutes = seconds // 60

    return (
        f"{minutes} minute"
        if minutes == 1
        else f"{minutes} minutes"
    )


async def handle_notification_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    value: str,
):
    query = update.callback_query
    db = SessionLocal()

    try:
        cooldown_seconds = int(value)

        if cooldown_seconds == 0:
            mode = "once"
        else:
            mode = "repeat"

        settings = update_notification_settings(
            db=db,
            mode=mode,
            cooldown_seconds=cooldown_seconds,
        )

        mode_text = (
            "Notify Once"
            if settings.notification_mode == "once"
            else "Repeat Reminder"
        )

        cooldown_text = format_cooldown(
            settings.notification_cooldown
        )

        await query.message.reply_text(
            "✅ <b>Notification Settings Updated</b>\n\n"
            f"🔔 Mode: <b>{mode_text}</b>\n"
            f"⏱ Cooldown: <b>{cooldown_text}</b>",
            parse_mode="HTML",
            reply_markup=settings_keyboard(),
        )

    except ValueError:
        await query.message.reply_text(
            "❌ Invalid notification setting.",
            reply_markup=notification_cooldown_keyboard(),
        )

    except Exception as error:
        db.rollback()

        print(f"Notification settings error: {error}")

        await query.message.reply_text(
            "❌ Notification settings update nahi hui."
        )

    finally:
        db.close()