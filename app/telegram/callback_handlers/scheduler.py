from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.keyboards import settings_keyboard


from app.scheduler.scheduler import (
    enable_monitoring,
    disable_monitoring,
    get_scheduler_status,
    update_scheduler_interval,
)


async def handle_settings_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    action: str,
):
    query = update.callback_query

    # ---------------- SCHEDULER STATUS ----------------

    if action == "status":
        status = get_scheduler_status()

        scheduler_status = (
            "Running"
            if status["scheduler_running"]
            else "Stopped"
        )

        monitoring_status = (
            "ON"
            if status["monitoring_enabled"]
            else "OFF"
        )

        last_cycle_time = status["last_cycle_completed_at"]

        if last_cycle_time:
            last_cycle_text = last_cycle_time.strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )
        else:
            last_cycle_text = "Not completed yet"

        last_cycle_duration = status[
            "last_cycle_duration_seconds"
        ]

        if last_cycle_duration is None:
            duration_text = "Not available"
        else:
            duration_text = f"{last_cycle_duration} seconds"

        message = (
            "📊 <b>Scheduler Status</b>\n\n"
            f"⚙ Scheduler: <b>{scheduler_status}</b>\n"
            f"📡 Monitoring: <b>{monitoring_status}</b>\n"
            f"⏱ Interval: "
            f"<b>{status['interval_seconds']} seconds</b>\n"
            f"👷 Workers: <b>{status['workers']}</b>\n"
            f"📦 Active Products: "
            f"<b>{status['active_products']}</b>\n"
            f"🕒 Last Cycle: <b>{last_cycle_text}</b>\n"
            f"⌛ Cycle Duration: <b>{duration_text}</b>"
        )

        await query.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=settings_keyboard(),
        )

    # ---------------- ENABLE MONITORING ----------------

    elif action == "enable":
        enable_monitoring()

        await query.message.reply_text(
            "▶️ <b>Monitoring Enabled</b>\n\n"
            "The scheduler will now check active products.",
            parse_mode="HTML",
            reply_markup=settings_keyboard(),
        )

    # ---------------- DISABLE MONITORING ----------------

    elif action == "disable":
        disabled = disable_monitoring()

        if disabled:
            message = (
                "⏸️ <b>Monitoring Disabled</b>\n\n"
                "Automatic product checking has been paused."
            )
        else:
            message = (
                "⚠️ <b>Scheduler job not found.</b>\n\n"
                "Monitoring may already be stopped."
            )

        await query.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=settings_keyboard(),
        )


async def handle_interval_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    value: str,
):
    query = update.callback_query

    try:
        seconds = int(value)
    except ValueError:
        await query.message.reply_text(
            "❌ Invalid scheduler interval."
        )
        return

    updated = update_scheduler_interval(seconds)

    if updated:
        if seconds < 60:
            interval_text = f"{seconds} seconds"
        else:
            minutes = seconds // 60

            interval_text = (
                f"{minutes} minute"
                if minutes == 1
                else f"{minutes} minutes"
            )

        await query.message.reply_text(
            "✅ <b>Scheduler Interval Updated</b>\n\n"
            f"New Interval: <b>{interval_text}</b>",
            parse_mode="HTML",
            reply_markup=settings_keyboard(),
        )

    else:
        await query.message.reply_text(
            "❌ Scheduler interval update nahi hua.\n"
            "Scheduler job start hona chahiye."
        )