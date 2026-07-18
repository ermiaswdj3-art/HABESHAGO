from telegram import Update
from telegram.ext import ContextTypes

from app.database.ride_repository import (
    get_latest_confirmed_ride,
    get_ride_status,
)

from app.constants.ride_status import (
    ACCEPTED,
    DRIVER_ARRIVING,
    DRIVER_ARRIVED,
    TRIP_STARTED,
    TRIP_COMPLETED,
)


async def ride_status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Show the passenger's latest ride status
    using clear, user-friendly messages.
    """

    if update.message is None:
        return

    passenger_id = update.effective_user.id

    ride = get_latest_confirmed_ride(passenger_id)

    if ride is None:
        await update.message.reply_text(
            "📍 Ride Status\n\n"
            "❌ You don't have an active ride right now.\n\n"
            "You can request a new ride whenever you're ready."
        )
        return

    ride_id = ride[0]
    status = get_ride_status(ride_id)

    status_messages = {
        ACCEPTED: (
            "✅ Your driver accepted the ride.\n\n"
            "🚖 The driver is preparing to come to your "
            "pickup location."
        ),
        DRIVER_ARRIVING: (
            "🚗 Your driver is on the way.\n\n"
            "⏳ Please remain near your pickup location."
        ),
        DRIVER_ARRIVED: (
            "📍 Your driver has arrived.\n\n"
            "🚶 Please proceed to the pickup point."
        ),
        TRIP_STARTED: (
            "🚕 Your trip is currently in progress.\n\n"
            "🛡 Have a safe and pleasant journey with "
            "HABESHAGO 🇪🇹"
        ),
        TRIP_COMPLETED: (
            "🏁 Your trip has been completed.\n\n"
            "🙏 Thank you for riding with HABESHAGO!"
        ),
    }

    message = status_messages.get(status)

    if message is None:
        message = (
            "ℹ️ Your ride status is being updated.\n\n"
            f"Current system status: {status}"
        )

    await update.message.reply_text(
        "📍 Current Ride Status\n\n"
        f"{message}"
    )