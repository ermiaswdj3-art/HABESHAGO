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


async def ride_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show the passenger's current ride status.
    """

    passenger_id = update.effective_user.id

    ride = get_latest_confirmed_ride(passenger_id)

    if ride is None:
        await update.message.reply_text(
            "❌ You don't have an active ride."
        )
        return

    ride_id = ride[0]

    status = get_ride_status(ride_id)

    status_messages = {
        ACCEPTED: "🚖 Driver accepted your ride.",
        DRIVER_ARRIVING: "🚗 Driver is on the way.",
        DRIVER_ARRIVED: "📍 Driver has arrived.",
        TRIP_STARTED: "🚕 Your trip is in progress.",
        TRIP_COMPLETED: "🏁 Trip completed.",
    }

    await update.message.reply_text(
        "📍 Current Ride Status\n\n"
        f"{status_messages.get(status, status)}"
    )