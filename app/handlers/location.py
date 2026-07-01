from telegram import Update
from telegram.ext import ContextTypes


async def receive_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location

    latitude = location.latitude
    longitude = location.longitude

    await update.message.reply_text(
        f"✅ Pickup location received!\n\n"
        f"Latitude: {latitude}\n"
        f"Longitude: {longitude}"
    )