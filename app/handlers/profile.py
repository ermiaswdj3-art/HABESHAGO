from telegram import Update
from telegram.ext import ContextTypes

from app.database.passenger_repository import get_passenger
from app.database.driver_repository import get_driver_by_telegram_id


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ==========================================
    # DRIVER PROFILE
    # ==========================================

    driver = get_driver_by_telegram_id(user_id)

    if driver is not None:

        (
            full_name,
            phone_number,
            vehicle,
            vehicle_year,
            vehicle_color,
            plate_number,
            rating,
            is_available,
        ) = driver

        status = "🟢 Available" if is_available else "🔴 Offline"

        await update.message.reply_text(
            "🚖 Driver Profile\n\n"
            f"👤 Name: {full_name}\n"
            f"📞 Phone: {phone_number}\n"
            f"🚗 Vehicle: {vehicle}\n"
            f"📅 Year: {vehicle_year}\n"
            f"🎨 Color: {vehicle_color}\n"
            f"🔢 Plate: {plate_number}\n"
            f"⭐ Rating: {rating}\n"
            f"{status}"
        )

        return

    # ==========================================
    # PASSENGER PROFILE
    # ==========================================

    passenger = get_passenger(user_id)

    if passenger is not None:

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

        return

    # ==========================================
    # NO PROFILE FOUND
    # ==========================================

    await update.message.reply_text(
        "❌ No passenger or driver profile was found."
    )