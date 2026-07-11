from telegram import Update
from telegram.ext import ContextTypes

from app.state.active_ride_state import active_rides
from app.services.tracking_service import (
    update_driver_location,
)


async def share_live_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Receive the driver's current GPS location.
    """

    driver_id = update.effective_user.id

    if driver_id not in active_rides:

        await update.message.reply_text(
            "❌ You don't have an active ride."
        )
        return

    if update.message.location is None:

        await update.message.reply_text(
            "📍 Please share your current location."
        )
        return

    passenger_id = active_rides[driver_id]["passenger_id"]

    latitude = update.message.location.latitude
    longitude = update.message.location.longitude

    update_driver_location(
        driver_id,
        passenger_id,
        latitude,
        longitude,
    )

    await update.message.reply_text(
        "📡 Live location updated successfully."
    )