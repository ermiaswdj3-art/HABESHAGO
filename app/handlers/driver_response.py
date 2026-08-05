"""
HABESHAGO Driver Ride Response Handlers

Processes driver acceptance and rejection through the
canonical persistent Ride Offer Platform.
"""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from app.constants.ride_status import (
    ACCEPTED,
)

from app.database.driver_repository import (
    get_driver_by_id,
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

from app.services.driver_availability_service import (
    make_driver_unavailable,
)

from app.services.eta_service import (
    calculate_eta,
)

from app.services.idempotency_service import (
    is_duplicate_action,
)

from app.services.progress_service import (
    send_driver_progress,
)

from app.services.ride_offer_service import (
    get_driver_pending_offer,
    reject_driver_ride_offer,
)

from app.state.active_ride_state import (
    active_rides,
)

from app.services.ride_offer_acceptance_service import (
    accept_offer_and_create_ride,
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
    Accept one canonical pending ride offer.

    The persistent Ride Offer is authoritative.
    Temporary dictionaries remain compatibility caches.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    # ==========================================
    # DUPLICATE-ACTION PROTECTION
    # ==========================================

    if is_duplicate_action(
        driver_id,
        "accept_ride",
    ):
        await update.message.reply_text(
            "⏳ Your ride acceptance is already "
            "being processed."
        )
        return

    # ==========================================
    # PREVENT MULTIPLE ACTIVE RIDES
    # ==========================================

    if driver_id in active_rides:
        await update.message.reply_text(
            "❌ You already have an active ride.\n\n"
            "Please complete your current ride "
            "before accepting another.",
            reply_markup=get_driver_menu(),
        )
        return

    # ==========================================
    # LOAD CANONICAL PENDING OFFER
    # ==========================================

    offer = get_driver_pending_offer(
        driver_id
    )

    if offer is None:
        pending_driver_requests.pop(
            driver_id,
            None,
        )

        await update.message.reply_text(
            "❌ No active ride offer is available.\n\n"
            "The offer may have expired, been cancelled, "
            "or already been resolved.",
            reply_markup=get_driver_menu(),
        )
        return

    request = {
        "offer_id": offer["offer_id"],
        "offer_reference": (
            offer["offer_reference"]
        ),
        "passenger_id": offer["passenger_id"],
        "pickup": (
            offer["pickup"]["latitude"],
            offer["pickup"]["longitude"],
        ),
        "destination": (
            offer["destination"]["latitude"],
            offer["destination"]["longitude"],
        ),
        "distance": offer["distance"],
        "pickup_distance": (
            offer["pickup_distance"]
        ),
        "pickup_eta": offer["pickup_eta"],
        "trip_eta": offer["trip_eta"],
        "fare": offer["fare"],
        "payment_method": (
            offer["payment_method"]
        ),
        "service_type": offer["service_type"],
    }

    passenger_id = request["passenger_id"]

        # ==========================================
    # ATOMIC OFFER ACCEPTANCE
    # ==========================================

    try:
        acceptance = (
            accept_offer_and_create_ride(
                offer_id=request["offer_id"],
                driver_id=driver_id,
            )
        )

    except ValueError as error:
        pending_driver_requests.pop(
            driver_id,
            None,
        )

        await update.message.reply_text(
            "❌ This ride offer can no longer "
            "be accepted.\n\n"
            f"{error}",
            reply_markup=get_driver_menu(),
        )
        return

    # ==========================================
    # LOAD ATOMIC ACCEPTANCE RESULT
    # ==========================================

    ride_id = acceptance["ride_id"]

    accepted_offer = {
        "offer_id": acceptance["offer_id"],
        "offer_reference": (
            acceptance["offer_reference"]
        ),
    }

    # ==========================================
    # CREATE CANONICAL ACTIVE ASSIGNMENT
    # ==========================================

    active_rides[driver_id] = {
        "ride_id": ride_id,
        "offer_id": (
            accepted_offer["offer_id"]
        ),
        "offer_reference": (
            accepted_offer["offer_reference"]
        ),
        "passenger_id": passenger_id,
        "pickup": request["pickup"],
        "destination": request["destination"],
        "distance": request["distance"],
        "pickup_distance": request[
            "pickup_distance"
        ],
        "pickup_eta": request[
            "pickup_eta"
        ],
        "trip_eta": request[
            "trip_eta"
        ],
        "fare": request["fare"],
        "payment_method": request[
            "payment_method"
        ],
        "service_type": request.get(
            "service_type",
            "fuel",
        ),
        "status": ACCEPTED,
        "recovered": False,
    }

    # ==========================================
    # DRIVER IS NOW BUSY
    # ==========================================

    try:
        make_driver_unavailable(
            driver_id
        )

    except ValueError as error:
        active_rides.pop(
            driver_id,
            None,
        )

        await update.message.reply_text(
            "❌ The ride could not be activated.\n\n"
            f"{error}",
            reply_markup=get_driver_menu(),
        )
        return

    # ==========================================
    # LOAD DRIVER PROFILE
    # ==========================================

    driver = get_driver_by_id(
        driver_id
    )

    if driver is None:
        await update.message.reply_text(
            "❌ Driver profile could not be found.",
            reply_markup=get_driver_menu(),
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
            f"🆔 Offer Reference: "
            f"{accepted_offer['offer_reference']}\n\n"
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

    # Start the temporary passenger progress task.
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
        f"🆔 Offer Reference: "
        f"{accepted_offer['offer_reference']}\n\n"
        "Drive safely to the passenger's "
        "pickup location.\n\n"
        "When you arrive, tap 📍 Arrived.",
        reply_markup=get_trip_status_keyboard(),
    )

    # ==========================================
    # CLEAN UP TEMPORARY MEMORY
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
    Reject one canonical pending ride offer.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    # ==========================================
    # LOAD CANONICAL PENDING OFFER
    # ==========================================

    offer = get_driver_pending_offer(
        driver_id
    )

    if offer is None:
        pending_driver_requests.pop(
            driver_id,
            None,
        )

        await update.message.reply_text(
            "❌ No active ride offer is available.\n\n"
            "The offer may have expired, been cancelled, "
            "or already been resolved.",
            reply_markup=get_driver_menu(),
        )
        return

    passenger_id = offer["passenger_id"]

    # ==========================================
    # REJECT CANONICAL OFFER
    # ==========================================

    try:
        rejected_offer = (
            reject_driver_ride_offer(
                offer["offer_id"]
            )
        )

    except ValueError as error:
        await update.message.reply_text(
            "❌ This ride offer can no longer "
            "be rejected.\n\n"
            f"{error}",
            reply_markup=get_driver_menu(),
        )
        return

    # ==========================================
    # NOTIFY PASSENGER
    # ==========================================

    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "😔 The driver declined your ride.\n\n"
            f"🆔 Offer Reference: "
            f"{rejected_offer['offer_reference']}\n\n"
            "Please request another ride."
        ),
        reply_markup=get_main_menu(),
    )

    # ==========================================
    # CLEAN UP TEMPORARY MEMORY
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
        f"🆔 Offer Reference: "
        f"{rejected_offer['offer_reference']}\n\n"
        "You are ready to receive another "
        "ride request.",
        reply_markup=get_driver_menu(),
    )