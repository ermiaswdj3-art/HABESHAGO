from telegram import Update
from telegram.ext import ContextTypes

from app.database.driver_repository import (
    get_driver_by_telegram_id,
)


async def show_driver_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the Driver Dashboard.
    """

    user_id = update.effective_user.id

    driver = get_driver_by_telegram_id(user_id)

    if driver is None:

        await update.message.reply_text(
            "❌ Driver profile not found.\n\n"
            "Please register as a driver first."
        )

        return

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

    status = (
        "🟢 Online"
        if is_available
        else "🔴 Offline"
    )

    await update.message.reply_text(
        "🚖 HABESHAGO Driver Dashboard\n\n"
        f"👤 Driver: {full_name}\n"
        f"🚗 Vehicle: {vehicle}\n"
        f"📅 Year: {vehicle_year}\n"
        f"🎨 Color: {vehicle_color}\n"
        f"🔢 Plate: {plate_number}\n"
        f"⭐ Rating: {rating}\n"
        f"{status}\n\n"
        "━━━━━━━━━━━━━━\n"
        "📍 Ready to receive rides."
    )