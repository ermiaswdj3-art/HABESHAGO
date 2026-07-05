from telegram import Update
from telegram.ext import ContextTypes

from app.database.driver_repository import register_driver


async def become_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Register the current Telegram user as a driver.
    """

    user = update.effective_user

    telegram_id = user.id
    full_name = user.full_name

    try:
        register_driver(
            telegram_id=telegram_id,
            full_name=full_name,
            phone_number="0994632089",
            vehicle="Toyota Vitz",
            vehicle_color="White",
            plate_number=f"TG-{telegram_id}",
            latitude=8.958108,
            longitude=38.772987,
        )

        await update.message.reply_text(
            "🎉 Congratulations!\n\n"
            "🚖 You are now registered as a HABESHAGO driver.\n\n"
            "You will soon begin receiving ride requests."
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Driver registration failed:\n\n{e}"
        )