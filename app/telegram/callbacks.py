from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.callback_handlers.scheduler import (
    handle_settings_callback,
    handle_interval_callback,
)

from app.telegram.callback_handlers.products import (
    handle_product_callback,
    handle_edit_callback,
)

from app.telegram.callback_handlers.settings import (
    handle_settings_menu_callback,
)

from app.telegram.callback_handlers.notification import (
    handle_notification_callback,
)

async def callback_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    data = query.data

    if not data:
        return

    parts = data.split(":")

    # =====================================================
    # TWO-PART CALLBACKS
    # Examples:
    # settings:status
    # settings:interval
    # interval:30
    # cooldown:60
    # =====================================================

    if len(parts) == 2:
        module = parts[0]
        action = parts[1]

        if module == "settings":

            if action in {"interval", "cooldown", "back"}:
                await handle_settings_menu_callback(
                    update,
                    context,
                    action,
                )

            else:
                await handle_settings_callback(
                    update,
                    context,
                    action,
                )

        elif module == "interval":
            await handle_interval_callback(
                update,
                context,
                action,
            )
            
        elif module == "cooldown":
            await handle_notification_callback(
                update,
                context,
                action,
            )

        return

    # =====================================================
    # THREE-PART CALLBACKS
    # Examples:
    # product:edit:5
    # product:delete:5
    # edit:name:5
    # =====================================================

    if len(parts) != 3:
        return

    module = parts[0]
    action = parts[1]

    try:
        product_id = int(parts[2])

    except ValueError:
        await query.message.reply_text(
            "❌ Invalid Product ID."
        )
        return

    if module == "product":
        await handle_product_callback(
            update,
            context,
            action,
            product_id,
        )

    elif module == "edit":
        await handle_edit_callback(
            update,
            context,
            action,
            product_id,
        )