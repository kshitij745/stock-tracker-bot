from telegram import Update
from telegram.ext import ContextTypes

from app.database.database import SessionLocal
from app.models.product import Product
from app.telegram.keyboards import product_buttons


async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = SessionLocal()

    products = db.query(Product).order_by(Product.id.desc()).all()

    db.close()

    if not products:

        await update.message.reply_text(
            "📦 No Products Found."
        )

        return

    for product in products:

        stock = "✅ In Stock" if product.in_stock else "❌ Out Of Stock"

        monitoring = "✅ ON" if product.is_active else "❌ OFF"

        text = (
            f"📱 <b>{product.product_name}</b>\n\n"
            f"🏪 {product.store_name}\n"
            f"📦 {stock}\n"
            f"🔄 Monitoring : {monitoring}"
        )

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=product_buttons(product.id)
        )