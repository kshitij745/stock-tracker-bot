from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.product import Product
from app.telegram.keyboards import main_menu
from app.telegram.states import (
    PRODUCT_NAME,
    STORE,
    PRODUCT_URL,
    AFFILIATE_URL,
)


STORE_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["Amazon", "Flipkart"],
        ["Croma", "Reliance Digital"],
        ["OnePlus Store"]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

AFFILIATE_KEYBOARD = ReplyKeyboardMarkup(
    [["Skip"]],
    resize_keyboard=True,
    one_time_keyboard=True
)


async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📱 Enter Product Name",
        reply_markup=ReplyKeyboardRemove()
    )
    return PRODUCT_NAME


async def product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product_name"] = update.message.text

    await update.message.reply_text(
        "🏪 Select Store",
        reply_markup=STORE_KEYBOARD
    )

    return STORE


async def store(update: Update, context: ContextTypes.DEFAULT_TYPE):

    valid_stores = [
        "Amazon",
        "Flipkart",
        "Croma",
        "Reliance Digital",
        "OnePlus Store"
    ]

    if update.message.text not in valid_stores:
        await update.message.reply_text(
            "❌ Invalid Store.\n\nPlease select from the keyboard."
        )
        return STORE

    context.user_data["store_name"] = update.message.text

    await update.message.reply_text(
        "🔗 Send Product URL",
        reply_markup=ReplyKeyboardRemove()
    )

    return PRODUCT_URL


async def product_url(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["product_url"] = update.message.text

    await update.message.reply_text(
        "💰 Send Affiliate URL\n\nOr press Skip.",
        reply_markup=AFFILIATE_KEYBOARD
    )

    return AFFILIATE_URL


async def affiliate_url(update: Update, context: ContextTypes.DEFAULT_TYPE):

    affiliate = update.message.text

    if affiliate.lower() == "skip":
        affiliate = None

    db: Session = SessionLocal()

    product = Product(
        product_name=context.user_data["product_name"],
        store_name=context.user_data["store_name"],
        product_url=context.user_data["product_url"],
        affiliate_url=affiliate,
        is_active=True
    )

    db.add(product)
    db.commit()
    db.close()

    context.user_data.clear()

    await update.message.reply_text(
        "✅ Product Saved Successfully.",
        reply_markup=main_menu()
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Cancelled",
        reply_markup=main_menu()
    )

    return ConversationHandler.END