from telegram import Update
from telegram.ext import ContextTypes

from app.database.database import SessionLocal
from app.models.product import Product


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db = SessionLocal()

    try:
        total_products = db.query(Product).count()

        active_products = db.query(Product).filter(
            Product.is_active == True
        ).count()

        inactive_products = db.query(Product).filter(
            Product.is_active == False
        ).count()

        in_stock = db.query(Product).filter(
            Product.in_stock == True
        ).count()

        out_of_stock = db.query(Product).filter(
            Product.in_stock == False
        ).count()

        amazon = db.query(Product).filter(Product.store_name == "Amazon").count()
        flipkart = db.query(Product).filter(Product.store_name == "Flipkart").count()
        croma = db.query(Product).filter(Product.store_name == "Croma").count()
        reliance = db.query(Product).filter(Product.store_name == "Reliance Digital").count()
        oneplus = db.query(Product).filter(Product.store_name == "OnePlus Store").count()

        message = (
            "📊 <b>Stock Tracker Statistics</b>\n\n"
            f"📦 <b>Total Products:</b> {total_products}\n\n"
            f"✅ <b>In Stock:</b> {in_stock}\n"
            f"❌ <b>Out Of Stock:</b> {out_of_stock}\n\n"
            f"🟢 <b>Active Monitoring:</b> {active_products}\n"
            f"🔴 <b>Disabled Monitoring:</b> {inactive_products}\n\n"
            "🏪 <b>Store Wise</b>\n\n"
            f"🛒 Amazon: {amazon}\n"
            f"🛍 Flipkart: {flipkart}\n"
            f"🏪 Croma: {croma}\n"
            f"🏬 Reliance Digital: {reliance}\n"
            f"📱 OnePlus Store: {oneplus}"
        )

        await update.message.reply_text(
            message,
            parse_mode="HTML"
        )

    finally:
        db.close()