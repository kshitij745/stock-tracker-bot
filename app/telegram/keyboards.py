from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_menu():

    keyboard = [
        ["➕ Add Product", "📋 Products"],
        ["🔍 Search Product", "🔄 Check All"],
        ["📊 Statistics", "⚙ Settings"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )


def product_buttons(product_id: int):

    keyboard = [
        [
            InlineKeyboardButton(
                "✏ Edit",
                callback_data=f"product:edit:{product_id}",
            ),
            InlineKeyboardButton(
                "🔗 Affiliate",
                callback_data=f"product:affiliate:{product_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                "🔄 Check",
                callback_data=f"product:check:{product_id}",
            ),
            InlineKeyboardButton(
                "🗑 Delete",
                callback_data=f"product:delete:{product_id}",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def edit_product_keyboard(product_id: int):

    keyboard = [
        [
            InlineKeyboardButton(
                "📝 Product Name",
                callback_data=f"edit:name:{product_id}",
            )
        ],
        [
            InlineKeyboardButton(
                "🏪 Store",
                callback_data=f"edit:store:{product_id}",
            )
        ],
        [
            InlineKeyboardButton(
                "🔗 Product URL",
                callback_data=f"edit:url:{product_id}",
            )
        ],
        [
            InlineKeyboardButton(
                "💰 Affiliate URL",
                callback_data=f"edit:affiliate:{product_id}",
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data=f"edit:cancel:{product_id}",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def settings_keyboard():

    keyboard = [
        [
            InlineKeyboardButton(
                "📊 Scheduler Status",
                callback_data="settings:status",
            )
        ],
        [
            InlineKeyboardButton(
                "▶ Enable Monitoring",
                callback_data="settings:enable",
            ),
            InlineKeyboardButton(
                "⏸ Disable Monitoring",
                callback_data="settings:disable",
            ),
        ],
        [
            InlineKeyboardButton(
                "🔄 Scheduler Interval",
                callback_data="settings:interval",
            )
        ],
        [
            InlineKeyboardButton(
                "🔔 Notification Cooldown",
                callback_data="settings:cooldown",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def scheduler_interval_keyboard():

    keyboard = [
        [
            InlineKeyboardButton(
                "10 Seconds",
                callback_data="interval:10",
            ),
            InlineKeyboardButton(
                "30 Seconds",
                callback_data="interval:30",
            ),
        ],
        [
            InlineKeyboardButton(
                "1 Minute",
                callback_data="interval:60",
            ),
            InlineKeyboardButton(
                "2 Minutes",
                callback_data="interval:120",
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="settings:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def notification_cooldown_keyboard():

    keyboard = [
        [
            InlineKeyboardButton(
                "Notify Once",
                callback_data="cooldown:0",
            )
        ],
        [
            InlineKeyboardButton(
                "10 Seconds",
                callback_data="cooldown:10",
            ),
            InlineKeyboardButton(
                "1 Minute",
                callback_data="cooldown:60",
            ),
        ],
        [
            InlineKeyboardButton(
                "5 Minutes",
                callback_data="cooldown:300",
            ),
            InlineKeyboardButton(
                "30 Minutes",
                callback_data="cooldown:1800",
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅ Back",
                callback_data="settings:back",
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)