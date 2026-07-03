from telegram import Update
from telegram.ext import ContextTypes

from app.database.passenger_repository import update_phone_number


async def set_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) != 1:
        await update.message.reply_text(
            "Usage:\n"
            "/setphone +251911234567"
        )
        return

    phone_number = context.args[0]

    update_phone_number(
        telegram_id=user_id,
        phone_number=phone_number,
    )

    await update.message.reply_text(
        "✅ Your phone number has been updated successfully!"
    )