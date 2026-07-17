from telegram import Update
from telegram.ext import ContextTypes

from app.database.passenger_repository import get_passenger

from app.database.driver_repository import (
    get_driver_profile,
)

from app.database.ride_repository import (
    get_rides_by_passenger,
)

async def show_profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Show the current user's driver or passenger profile.
    """

    user_id = update.effective_user.id

    # ==========================================
    # DRIVER PROFILE
    # ==========================================

    driver = get_driver_profile(user_id)

    if driver is not None:

        (
            full_name,
            phone_number,
            vehicle,
            vehicle_year,
            vehicle_color,
            plate_number,
            rating,
            is_online,
            is_available,
        ) = driver

        online_status = (
            "🟢 Online"
            if is_online
            else "🔴 Offline"
        )

        availability_status = (
            "✅ Available"
            if is_available
            else "🚕 Busy / Unavailable"
        )

        await update.message.reply_text(
            "🚖 Driver Profile\n\n"
            f"👤 Name: {full_name}\n"
            f"📞 Phone: {phone_number}\n"
            f"🚗 Vehicle: {vehicle}\n"
            f"📅 Year: {vehicle_year}\n"
            f"🎨 Color: {vehicle_color}\n"
            f"🔢 Plate: {plate_number}\n"
            f"⭐ Rating: {rating}\n\n"
            f"📡 Status: {online_status}\n"
            f"🚖 Availability: {availability_status}"
        )

        return

    # ==========================================
    # PASSENGER PROFILE
    # ==========================================

    passenger = get_passenger(user_id)

    if passenger is not None:

        (
            telegram_id,
            full_name,
            phone_number,
            created_at,
        ) = passenger

        if phone_number is None:
            phone_number = "Not set"

        rides = get_rides_by_passenger(user_id)

        total_rides = len(rides)

        completed_rides = sum(
            1
            for ride in rides
            if ride[4] in ("TRIP_COMPLETED", "RATED")
        )

        total_spent = sum(
            ride[3]
            for ride in rides
            if ride[4] in ("TRIP_COMPLETED", "RATED")
        )

        await update.message.reply_text(
            "👤 Passenger Profile\n\n"
            f"🆔 Telegram ID: {telegram_id}\n"
            f"👤 Name: {full_name}\n"
            f"📞 Phone: {phone_number}\n"
            f"📅 Member Since: {created_at}\n\n"
            "📊 Ride Statistics\n"
            f"🚖 Total Rides: {total_rides}\n"
            f"✅ Completed Rides: {completed_rides}\n"
            f"💰 Total Amount Spent: {total_spent:.2f} ETB"
        )

        return
    
    # ==========================================
    # NO PROFILE FOUND
    # ==========================================

    await update.message.reply_text(
        "❌ No passenger or driver profile was found."
    )