import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.database.driver_repository import (
    register_driver,
    update_driver_location,
)

from app.database.passenger_places_repository import (
    save_recent_place,
)

from app.keyboards.confirmation import (
    get_confirmation_keyboard,
)

from app.keyboards.destination_menu import (
    get_destination_menu,
)

from app.keyboards.driver_dashboard import (
    get_driver_dashboard_keyboard,
)

from app.services.distance_service import (
    calculate_distance,
)

from app.services.geocoding_service import (
    get_location_details,
)

from app.services.live_location_service import (
    record_live_location,
)

from app.services.pricing_service import (
    calculate_fare,
)

from app.state.driver_registration_state import (
    driver_registration_state,
)

from app.state.ride_state import (
    ride_requests,
)

logger = logging.getLogger(__name__)


async def receive_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Route received Telegram locations to:

    - driver location updates;
    - driver registration;
    - passenger pickup selection;
    - passenger destination selection.
    """

    if update.message is None or update.message.location is None:
        return

    user_id = update.effective_user.id
    user = update.effective_user
    location = update.message.location

    latitude = location.latitude
    longitude = location.longitude

    # ==========================================
    # DRIVER LIVE LOCATION UPDATE
    # ==========================================

    if context.user_data.get("driver_update_location") is True:
        # Save the coordinates in the database
        # for long-term persistence.
        update_driver_location(
            user_id,
            latitude,
            longitude,
        )

        # Record the same coordinates in the
        # Live Location Platform with a fresh
        # timestamp and LIVE status.
        live_location = record_live_location(
            entity_id=user_id,
            latitude=latitude,
            longitude=longitude,
        )

        context.user_data["driver_update_location"] = False

        await update.message.reply_text(
            "📍 Your live location has been updated successfully!\n\n"
            f"🟢 Location Status: {live_location.status}\n\n"
            "You are now eligible for intelligent dispatch "
            "while this location remains fresh.",
            reply_markup=get_driver_dashboard_keyboard(),
        )

        return

    # ==========================================
    # DRIVER REGISTRATION LOCATION
    # ==========================================

    if (
        user_id in driver_registration_state
        and driver_registration_state[user_id].get("step") == "location"
    ):
        state = driver_registration_state[user_id]

        register_driver(
            telegram_id=user.id,
            full_name=user.full_name,
            phone_number=state["phone_number"],
            vehicle=(f'{state["vehicle_brand"]} ' f'{state["vehicle_model"]}'),
            vehicle_year=int(state["vehicle_year"]),
            vehicle_color=state["vehicle_color"],
            plate_number=state["plate_number"],
            latitude=latitude,
            longitude=longitude,
        )

        record_live_location(
            entity_id=user_id,
            latitude=latitude,
            longitude=longitude,
        )

        del driver_registration_state[user_id]

        await update.message.reply_text(
            "✅ Driver application submitted!\n\n"
            "Your HABESHAGO driver profile has been saved "
            "successfully.\n\n"
            "📋 Registration Status\n"
            "Verification Pending\n\n"
            "🪪 Identity Verification\n"
            "Pending\n\n"
            "🚗 Vehicle Verification\n"
            "Pending\n\n"
            "You cannot receive ride requests until your "
            "application has been reviewed and approved.\n\n"
            "HABESHAGO will notify you when the verification "
            "process is complete."
        )

        return

    # ==========================================
    # PASSENGER PICKUP LOCATION
    # ==========================================

    if (
        user_id not in ride_requests
        or ride_requests[user_id].get("status") != "waiting_for_destination"
    ):
        pickup_details = await asyncio.to_thread(
            get_location_details,
            latitude,
            longitude,
            "en",
        )

        ride_requests[user_id] = {
            "pickup": (
                latitude,
                longitude,
            ),
            "pickup_name": pickup_details["short_name"],
            "pickup_full_name": pickup_details["full_name"],
            "destination": None,
            "destination_name": None,
            "destination_full_name": None,
            "status": "waiting_for_destination",
        }

        await update.message.reply_text(
            "✅ Pickup location received successfully!\n\n"
            f"📍 Pickup\n"
            f"{pickup_details['short_name']}\n\n"
            "Where would you like to go?\n\n"
            "Choose one of the options below.",
            reply_markup=get_destination_menu(),
        )

        return

    # ==========================================
    # PASSENGER DESTINATION LOCATION
    # ==========================================

    destination_details = await asyncio.to_thread(
        get_location_details,
        latitude,
        longitude,
        "en",
    )

    destination = (
        latitude,
        longitude,
    )

    ride_requests[user_id]["destination"] = destination

    ride_requests[user_id]["destination_name"] = destination_details["short_name"]

    ride_requests[user_id]["destination_full_name"] = destination_details["full_name"]

    ride_requests[user_id]["status"] = "completed"

    # Automatically save the manually shared
    # destination as a recent passenger place.
    save_recent_place(
        passenger_id=user_id,
        place_name=destination_details["short_name"],
        full_address=destination_details["full_name"],
        latitude=latitude,
        longitude=longitude,
    )

    pickup = ride_requests[user_id]["pickup"]

    pickup_name = ride_requests[user_id].get(
        "pickup_name",
        "Pickup location",
    )

    distance = calculate_distance(
        pickup[0],
        pickup[1],
        destination[0],
        destination[1],
    )

    fare = calculate_fare(distance)

    await update.message.reply_text(
        "🚕 Ride Summary\n\n"
        "📍 From\n"
        f"{pickup_name}\n\n"
        "🏁 To\n"
        f"{destination_details['short_name']}\n\n"
        "📏 Distance\n"
        f"{distance:.2f} km\n\n"
        "💰 Estimated Fare\n"
        f"{fare:.2f} ETB\n\n"
        "Would you like to confirm this ride?",
        reply_markup=get_confirmation_keyboard(),
    )
