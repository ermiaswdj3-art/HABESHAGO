from telegram import Update
from telegram.ext import ContextTypes

from app.database.driver_repository import (
    get_driver_profile,
)

from app.database.ride_repository import (
    get_driver_rides,
    get_rides_by_passenger,
)


async def show_rides(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Show ride history for a driver or passenger.
    """

    user_id = update.effective_user.id

    # ==========================================
    # DRIVER RIDE HISTORY
    # ==========================================

    driver = get_driver_profile(user_id)

    if driver is not None:
        rides = get_driver_rides(user_id)

        if not rides:
            await update.message.reply_text(
                "📭 You don't have any driver ride history yet."
            )
            return

        total_fare = 0.0
        completed_rides = 0

        status_map = {
            "REQUESTED": "⏳ Requested",
            "ACCEPTED": "✅ Accepted",
            "DRIVER_ARRIVING": "🚗 Driver Arriving",
            "DRIVER_ARRIVED": "📍 Driver Arrived",
            "TRIP_STARTED": "🚕 Trip Started",
            "TRIP_COMPLETED": "🏁 Completed",
            "RATED": "⭐ Rated",
        }

        message = "📋 Driver Ride History\n\n"

        for ride in rides:
            (
                ride_id,
                distance,
                fare,
                status,
                driver_rating,
            ) = ride

            display_status = status_map.get(status, status)

            total_fare += fare

            if status == "TRIP_COMPLETED":
                completed_rides += 1

            rating_text = (
                f"{driver_rating}/5"
                if driver_rating is not None
                else "Not rated"
            )

            message += (
                f"🚖 Ride #{ride_id}\n"
                f"📏 Distance: {distance:.2f} km\n"
                f"💰 Fare: {fare:.2f} ETB\n"
                f"📌 Status: {display_status}\n"
                f"⭐ Passenger Rating: {rating_text}\n\n"
            )

        message += (
            "━━━━━━━━━━━━━━\n"
            f"📊 Total Rides: {len(rides)}\n"
            f"✅ Completed Rides: {completed_rides}\n"
            f"💰 Total Ride Value: {total_fare:.2f} ETB"
        )

        await update.message.reply_text(message)
        return

    # ==========================================
    # PASSENGER RIDE HISTORY
    # ==========================================

    rides = get_rides_by_passenger(user_id)

    if not rides:
        await update.message.reply_text(
            "📭 You don't have any passenger ride history yet."
        )
        return

    status_map = {
        "REQUESTED": "⏳ Requested",
        "ACCEPTED": "✅ Accepted",
        "DRIVER_ARRIVING": "🚗 Driver Arriving",
        "DRIVER_ARRIVED": "📍 Driver Arrived",
        "TRIP_STARTED": "🚕 Trip Started",
        "TRIP_COMPLETED": "🏁 Completed",
        "RATED": "⭐ Rated",
    }

    total_spent = 0.0
    completed_rides = 0

    message = "📜 Passenger Ride History\n\n"

    for ride in rides:
        (
            ride_id,
            driver_id,
            distance,
            fare,
            status,
            driver_rating,
        ) = ride

        display_status = status_map.get(status, status)

        total_spent += fare

        if status in ("TRIP_COMPLETED", "RATED"):
            completed_rides += 1

        rating_text = (
            f"{driver_rating}/5"
            if driver_rating is not None
            else "Not rated"
        )

        message += (
            f"🚖 Ride #{ride_id}\n"
            f"👤 Driver ID: {driver_id}\n"
            f"📏 Distance: {distance:.2f} km\n"
            f"💰 Fare: {fare:.2f} ETB\n"
            f"📌 Status: {display_status}\n"
            f"⭐ Your Rating: {rating_text}\n\n"
    )

    message += (
        "━━━━━━━━━━━━━━\n"
        f"📊 Total Rides: {len(rides)}\n"
        f"✅ Completed Rides: {completed_rides}\n"
        f"💰 Total Amount Spent: {total_spent:.2f} ETB"
    )

    await update.message.reply_text(message)