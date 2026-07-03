from telegram import Update
from telegram.ext import ContextTypes

from app.database.passenger_repository import get_passenger


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    passenger = get_passenger(user_id)

    if passenger is None:
        await update.message.reply_text(
            "❌ Passenger profile not found."
        )
        return

    telegram_id, full_name, phone_number, created_at = passenger

    if phone_number is None:
        phone_number = "Not set"

    await update.message.reply_text(
        "👤 Passenger Profile\n\n"
        f"🆔 Telegram ID: {telegram_id}\n"
        f"👤 Name: {full_name}\n"
        f"📞 Phone: {phone_number}\n"
        f"📅 Member Since: {created_at}"
    )