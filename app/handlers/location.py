from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.location import get_location_keyboard
from app.keyboards.confirmation import get_confirmation_keyboard

from app.services.distance_service import calculate_distance
from app.services.pricing_service import calculate_fare

from app.state.ride_state import ride_requests
from app.state.driver_registration_state import driver_registration_state

from app.database.driver_repository import register_driver


async def receive_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📍 receive_location() was called")
    if update.message is None or update.message.location is None:
        return
    user_id = update.effective_user.id
    user = update.effective_user
    location = update.message.location

    print("\n========== LOCATION DEBUG ==========")
    print("User ID:", user_id)
    print("Driver registration state:", driver_registration_state)

    if user_id in driver_registration_state:
       print("Current step:", driver_registration_state[user_id]["step"])
    else:
       print("User is NOT in driver_registration_state")

    latitude = location.latitude
    longitude = location.longitude

    # ==========================================
    # DRIVER REGISTRATION LOCATION
    # ==========================================
    if (
        user_id in driver_registration_state
        and driver_registration_state[user_id]["step"] == "location"
    ):
        print("✅ Driver registration detected.")

        state = driver_registration_state[user_id]

        register_driver(
            telegram_id=user.id,
            full_name=user.full_name,
            phone_number=state["phone_number"],
            vehicle=f'{state["vehicle_brand"]} {state["vehicle_model"]}',
            vehicle_year=int(state["vehicle_year"]),
            vehicle_color=state["vehicle_color"],
            plate_number=state["plate_number"],
            latitude=latitude,
            longitude=longitude,
        )

        del driver_registration_state[user_id]

        await update.message.reply_text(
            "🎉 Congratulations!\n\n"
            "🚖 Your driver registration is complete!\n\n"
            "You are now available to receive ride requests."
        )

        return

    # ==========================================
    # PASSENGER RIDE LOCATION
    # ==========================================

    # First location = Pickup
    if (
        user_id not in ride_requests
        or ride_requests[user_id]["status"] != "waiting_for_destination"
    ):

        ride_requests[user_id] = {
            "pickup": (latitude, longitude),
            "destination": None,
            "status": "waiting_for_destination",
        }

        await update.message.reply_text(
            "✅ Pickup location received!\n\n"
            "Please share your destination location.",
            reply_markup=get_location_keyboard(
                "📍 Share Destination Location"
            ),
        )

    # Second location = Destination
    else:

        ride_requests[user_id]["destination"] = (
            latitude,
            longitude,
        )

        ride_requests[user_id]["status"] = "completed"

        pickup = ride_requests[user_id]["pickup"]
        destination = ride_requests[user_id]["destination"]

        distance = calculate_distance(
            pickup[0],
            pickup[1],
            destination[0],
            destination[1],
        )

        fare = calculate_fare(distance)

        await update.message.reply_text(
            "🚖 Ride Summary\n\n"
            f"📏 Estimated Distance: {distance:.2f} km\n"
            f"💰 Estimated Fare: {fare:.2f} ETB\n\n"
            "Would you like to confirm this ride?",
            reply_markup=get_confirmation_keyboard(),
        )