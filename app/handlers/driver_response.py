import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from app.constants.ride_status import (
    ACCEPTED,
)

from app.database.driver_repository import (
    get_driver_by_id,
    set_driver_unavailable,
)

from app.database.ride_repository import (
    save_ride,
)

from app.keyboards.driver_menu import (
    get_driver_menu,
)

from app.keyboards.main_menu import (
    get_main_menu,
)

from app.keyboards.ride_status import (
    get_ride_status_keyboard,
)

from app.keyboards.trip_status import (
    get_trip_status_keyboard,
)

from app.services.eta_service import (
    calculate_eta,
)

from app.services.progress_service import (
    send_driver_progress,
)

from app.state.active_ride_state import (
    active_rides,
)

from app.state.driver_state import (
    pending_driver_requests,
)

from app.state.ride_state import (
    ride_requests,
)


async def accept_ride(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Driver accepts a passenger's ride request.

    The accepted ride is saved to the database,
    accepted_at is recorded automatically, and
    the ride becomes active for the driver.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    # ==========================================
    # PREVENT MULTIPLE ACTIVE RIDES
    # ==========================================

    if driver_id in active_rides:
        await update.message.reply_text(
            "❌ You already have an active ride.\n\n"
            "Please complete your current ride "
            "before accepting another."
        )
        return

    # ==========================================
    # VERIFY PENDING REQUEST
    # ==========================================

    request = pending_driver_requests.get(
        driver_id
    )

    if request is None:
        await update.message.reply_text(
            "❌ No pending ride request."
        )
        return

    passenger_id = request["passenger_id"]

    # ==========================================
    # SAVE ACCEPTED RIDE
    # ==========================================

    ride_id = save_ride(
        passenger_id=passenger_id,
        driver_id=driver_id,
        pickup_latitude=request["pickup"][0],
        pickup_longitude=request["pickup"][1],
        destination_latitude=request[
            "destination"
        ][0],
        destination_longitude=request[
            "destination"
        ][1],
        distance=request["distance"],
        fare=request["fare"],
        status=ACCEPTED,
        service_type=request.get(
            "service_type",
            "fuel",
        ),
    )

    # save_ride() records:
    #
    # created_at
    # requested_at
    # accepted_at
    #
    # because this ride is saved with ACCEPTED.

    # ==========================================
    # DRIVER IS NOW BUSY
    # ==========================================

    set_driver_unavailable(
        driver_id
    )

    active_rides[driver_id] = {
        "ride_id": ride_id,
        "passenger_id": passenger_id,
        "pickup": request["pickup"],
        "destination": request["destination"],
        "distance": request["distance"],
        "fare": request["fare"],
        "service_type": request.get(
            "service_type",
            "fuel",
        ),
    }

    driver = get_driver_by_id(
        driver_id
    )

    if driver is None:
        await update.message.reply_text(
            "❌ Driver profile could not be found."
        )
        return

    eta = calculate_eta(
        request["pickup_distance"]
    )

    # ==========================================
    # NOTIFY PASSENGER
    # ==========================================

    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "🎉 Your ride has been accepted!\n\n"
            f"👤 Driver: {driver[1]}\n"
            f"⭐ Rating: {driver[6]}\n"
            f"🚗 Vehicle: {driver[3]}\n"
            f"🎨 Color: {driver[4]}\n"
            f"🔢 Plate: {driver[5]}\n\n"
            "🚖 Your driver is on the way.\n\n"
            f"⏱ Estimated arrival: {eta} minutes."
        ),
        reply_markup=get_ride_status_keyboard(),
    )

    # Start the temporary passenger progress
    # notification task.
    asyncio.create_task(
        send_driver_progress(
            context,
            passenger_id,
        )
    )

    # ==========================================
    # CONFIRM TO DRIVER
    # ==========================================

    await update.message.reply_text(
        "✅ Ride accepted successfully!\n\n"
        "Drive safely to the passenger's "
        "pickup location.\n\n"
        "When you arrive, tap 📍 Arrived.",
        reply_markup=get_trip_status_keyboard(),
    )

    # ==========================================
    # CLEAN UP PENDING MEMORY
    # ==========================================

    ride_requests.pop(
        passenger_id,
        None,
    )

    pending_driver_requests.pop(
        driver_id,
        None,
    )


async def decline_ride(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Driver declines a passenger's pending
    ride request.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    request = pending_driver_requests.get(
        driver_id
    )

    if request is None:
        await update.message.reply_text(
            "❌ No pending ride request.",
            reply_markup=get_driver_menu(),
        )
        return

    passenger_id = request["passenger_id"]

    # ==========================================
    # NOTIFY PASSENGER
    # ==========================================

    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "😔 The driver declined your ride.\n\n"
            "Please request another ride."
        ),
        reply_markup=get_main_menu(),
    )

    # ==========================================
    # CLEAN UP PENDING REQUEST
    # ==========================================

    pending_driver_requests.pop(
        driver_id,
        None,
    )

    ride_requests.pop(
        passenger_id,
        None,
    )

    # ==========================================
    # RESTORE DRIVER MENU
    # ==========================================

    await update.message.reply_text(
        "❌ Ride declined.\n\n"
        "You are ready to receive another "
        "ride request.",
        reply_markup=get_driver_menu(),
    )