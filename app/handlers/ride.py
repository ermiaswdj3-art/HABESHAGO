from telegram import Update
from telegram.ext import ContextTypes


async def request_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚖 Ride Request\n\n"
        "Please send your pickup location."
    )