import os
import asyncio

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)

from app.telegram.handlers import (
    start,
    add_product,
    product_name,
    store,
    product_url,
    affiliate_url,
    cancel,
    products,
    statistics,
    settings,
    check_all_products,
    search_product,
    search_result,
)

from app.telegram.handlers.text_router import text_router
from app.telegram.callbacks import callback_router

from app.telegram.states import (
    PRODUCT_NAME,
    STORE,
    PRODUCT_URL,
    AFFILIATE_URL,
    SEARCH_PRODUCT,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():

    application = Application.builder().token(BOT_TOKEN).build()

    # -------------------------------------------------
    # Commands
    # -------------------------------------------------

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    # -------------------------------------------------
    # Add Product Conversation
    # -------------------------------------------------

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^➕ Add Product$"),
                    add_product,
                )
            ],
            states={
                PRODUCT_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        product_name,
                    )
                ],

                STORE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        store,
                    )
                ],

                PRODUCT_URL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        product_url,
                    )
                ],

                AFFILIATE_URL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        affiliate_url,
                    )
                ],
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    cancel,
                )
            ],
        )
    )

    # -------------------------------------------------
    # Search Product Conversation
    # -------------------------------------------------

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^🔍 Search Product$"),
                    search_product,
                )
            ],
            states={
                SEARCH_PRODUCT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        search_result,
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    cancel,
                )
            ],
        )
    )

    # -------------------------------------------------
    # Products
    # -------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.Regex("^📋 Products$"),
            products,
        )
    )

    # -------------------------------------------------
    # Check All Products
    # -------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.Regex("^🔄 Check All$"),
            check_all_products,
        )
    )

   # -------------------------------------------------
   # Statistics
   # -------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.Regex("^📊 Statistics$"),
            statistics,
        )
    )

   # -------------------------------------------------
   # Settings
   # -------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.Regex("^⚙ Settings$"),
            settings,
        )
    )

   # -------------------------------------------------
   # Callback Buttons
   # -------------------------------------------------

    application.add_handler(
        CallbackQueryHandler(
            callback_router,
        )
    )

    # -------------------------------------------------
    # Text Router
    # -------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_router,
        )
    )

    print("✅ Telegram Admin Bot Started")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    await asyncio.Event().wait()


def start_bot():
    asyncio.run(main())