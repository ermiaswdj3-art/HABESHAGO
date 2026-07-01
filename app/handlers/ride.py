from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes


async def request_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📍 Share Pickup Location", request_location=True)]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(
        "🚖 Ride Request\n\n"
        "Please press the button below to share your pickup location.",
        reply_markup=reply_markup,
    )