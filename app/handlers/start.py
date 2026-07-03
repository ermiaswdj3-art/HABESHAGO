from telegram import Update
from telegram.ext import ContextTypes

from app.database.passenger_repository import register_passenger
from app.keyboards.main_menu import get_main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    telegram_id = user.id
    full_name = user.full_name

    # Automatically register the passenger
    register_passenger(
        telegram_id=telegram_id,
        full_name=full_name,
    )

    await update.message.reply_text(
        "🚖 Welcome to HABESHAGO!\n\n"
        "Your trusted Ethiopian ride and delivery platform.\n\n"
        "Please choose an option below:",
        reply_markup=get_main_menu(),
    )