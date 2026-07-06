from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def get_chat_id(update: Update, context):
    print("=" * 50)
    print(f"Chat ID : {update.effective_chat.id}")
    print(f"Chat Name : {update.effective_chat.title}")
    print("=" * 50)


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, get_chat_id))

print("Bot Started...")

app.run_polling()