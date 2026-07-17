from telegram import Update
from telegram.ext import ContextTypes

from app.state.driver_state import pending_driver_requests
from app.state.ride_state import ride_requests
from app.state.active_ride_state import active_rides

from app.database.driver_repository import (
    set_driver_unavailable,
    get_driver_by_id,
)

from app.database.ride_repository import (
    save_ride,
)

from app.keyboards.trip_status import (
    get_trip_status_keyboard,
)

from app.keyboards.main_menu import (
    get_main_menu,
)

from app.keyboards.driver_menu import (
    get_driver_menu,
)

from app.keyboards.ride_status import (
    get_ride_status_keyboard,
)

from app.constants.ride_status import (
    ACCEPTED,
)

import asyncio

from app.services.progress_service import (
    send_driver_progress,
)

from app.services.eta_service import calculate_eta


async def accept_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Driver accepts a passenger's ride request.
    """

    driver_id = update.effective_user.id

    if driver_id in active_rides:
        await update.message.reply_text(
            "❌ You already have an active ride.\n\n"
            "Please complete your current ride before accepting another."
        )
        return

    if driver_id not in pending_driver_requests:

        await update.message.reply_text(
            "❌ No pending ride request."
        )

        return

    request = pending_driver_requests[driver_id]

    # ==========================================
    # SAVE RIDE
    # ==========================================

    save_ride(
        passenger_id=request["passenger_id"],
        driver_id=driver_id,
        pickup_latitude=request["pickup"][0],
        pickup_longitude=request["pickup"][1],
        destination_latitude=request["destination"][0],
        destination_longitude=request["destination"][1],
        distance=request["distance"],
        fare=request["fare"],
        status=ACCEPTED,
    )

    # ==========================================
    # DRIVER IS NOW BUSY
    # ==========================================

    set_driver_unavailable(driver_id)

    active_rides[driver_id] = {
        "passenger_id": request["passenger_id"],
    }

    driver = get_driver_by_id(driver_id)

    eta = calculate_eta(request["pickup_distance"])

    # ==========================================
    # NOTIFY PASSENGER
    # ==========================================

    await context.bot.send_message(
        chat_id=request["passenger_id"],
        text=(
            "🎉 Your ride has been accepted!\n\n"
            f"👤 Driver: {driver[1]}\n"
            f"⭐ Rating: {driver[6]}\n"
            f"🚗 Vehicle: {driver[3]}\n"
            f"🎨 Color: {driver[4]}\n"
            f"🔢 Plate: {driver[5]}\n\n"
            f"🚖 Your driver is on the way.\n\n"
            f"⏱ Estimated arrival: {eta} minutes."
        ),
        reply_markup=get_ride_status_keyboard(),
    )
    asyncio.create_task(
        send_driver_progress(
            context,
            request["passenger_id"],
        )
    )
    # ==========================================
    # CONFIRM TO DRIVER
    # ==========================================

    await update.message.reply_text(
        "✅ Ride accepted successfully!\n\n"
        "Drive safely to the passenger's pickup location.\n"
        "When you arrive, tap 📍 Arrived.",
        reply_markup=get_trip_status_keyboard(),
    )

    # ==========================================
    # CLEAN UP MEMORY
    # ==========================================

    passenger_id = request["passenger_id"]

    if passenger_id in ride_requests:
        del ride_requests[passenger_id]

    del pending_driver_requests[driver_id]


async def decline_ride(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Driver declines a passenger's ride request.
    """

    driver_id = update.effective_user.id

    if driver_id in pending_driver_requests:

        request = pending_driver_requests[driver_id]

        # Notify passenger
        await context.bot.send_message(
            chat_id=request["passenger_id"],
            text=(
                "😔 Your driver declined the ride.\n\n"
                "Please request another ride."
            ),
            reply_markup=get_main_menu(),
        )

        del pending_driver_requests[driver_id]

    # Restore driver's normal dashboard
    await update.message.reply_text(
        "❌ Ride declined.\n\n"
        "You are ready to receive another ride request.",
        reply_markup=get_driver_menu(),
    )