from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.main_menu import get_main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚖 Welcome to HABESHAGO!\n\n"
        "Your trusted Ethiopian ride and delivery platform.\n\n"
        "Please choose an option below:",
        reply_markup=get_main_menu(),
    )