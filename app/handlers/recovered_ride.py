from telegram import Update
from telegram.ext import ContextTypes

from app.constants.ride_status import (
    ACCEPTED,
    DRIVER_ARRIVED,
    DRIVER_ARRIVING,
    TRIP_STARTED,
)

from app.keyboards.navigation import (
    get_destination_navigation_keyboard,
    get_pickup_navigation_keyboard,
)

from app.keyboards.trip_status import (
    get_trip_status_keyboard,
)

from app.state.active_ride_state import (
    active_rides,
)


async def show_recovered_ride(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Show a driver the unfinished ride recovered
    after a HABESHAGO restart.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    ride = active_rides.get(driver_id)

    if ride is None:
        await update.message.reply_text(
            "✅ You do not have a recovered active ride."
        )
        return

    ride_id = ride["ride_id"]
    passenger_id = ride["passenger_id"]
    pickup = ride["pickup"]
    destination = ride["destination"]
    status = ride.get("status", ACCEPTED)

    if status in (
        ACCEPTED,
        DRIVER_ARRIVING,
    ):
        await update.message.reply_text(
            "🔄 Active ride recovered successfully!\n\n"
            f"🆔 Ride ID: {ride_id}\n"
            f"👤 Passenger ID: {passenger_id}\n"
            f"📌 Status: {status}\n\n"
            "Continue driving to the passenger's "
            "pickup location.\n\n"
            "When you arrive, tap 📍 Arrived.",
            reply_markup=get_pickup_navigation_keyboard(
                pickup[0],
                pickup[1],
            ),
        )

        await update.message.reply_text(
            "Your ride controls are ready.",
            reply_markup=get_trip_status_keyboard(),
        )
        return

    if status == DRIVER_ARRIVED:
        await update.message.reply_text(
            "🔄 Active ride recovered successfully!\n\n"
            f"🆔 Ride ID: {ride_id}\n"
            "📌 Status: Driver Arrived\n\n"
            "Please wait for the passenger to board.\n\n"
            "When everyone is ready, tap 🚕 Start Trip.",
            reply_markup=get_trip_status_keyboard(),
        )
        return

    if status == TRIP_STARTED:
        await update.message.reply_text(
            "🔄 Active trip recovered successfully!\n\n"
            f"🆔 Ride ID: {ride_id}\n"
            "📌 Status: Trip Started\n\n"
            "Continue safely to the destination.",
            reply_markup=get_destination_navigation_keyboard(
                destination[0],
                destination[1],
            ),
        )

        await update.message.reply_text(
            "When you reach the destination, "
            "tap 🏁 Complete Ride.",
            reply_markup=get_trip_status_keyboard(),
        )
        return

    await update.message.reply_text(
        "⚠️ The recovered ride has an unsupported status.\n\n"
        f"Ride ID: {ride_id}\n"
        f"Status: {status}"
    )