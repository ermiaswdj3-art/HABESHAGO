from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.location import get_location_keyboard


async def request_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚖 Ride Request\n\n"
        "Please share your pickup location.",
        reply_markup=get_location_keyboard(
            "📍 Share Pickup Location"
        ),
    )