from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.location import get_location_keyboard
from app.services.distance_service import calculate_distance
from app.services.pricing_service import calculate_fare
from app.state.ride_state import ride_requests


async def receive_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    location = update.message.location

    latitude = location.latitude
    longitude = location.longitude

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

        # Calculate distance
        distance = calculate_distance(
            pickup[0],
            pickup[1],
            destination[0],
            destination[1],
        )

        # Calculate fare
        fare = calculate_fare(distance)

        await update.message.reply_text(
            "🎉 Ride Request Summary\n\n"
            f"📍 Pickup:\n"
            f"Latitude: {pickup[0]}\n"
            f"Longitude: {pickup[1]}\n\n"
            f"🏁 Destination:\n"
            f"Latitude: {destination[0]}\n"
            f"Longitude: {destination[1]}\n\n"
            f"📏 Estimated Distance: {distance:.2f} km\n"
            f"💰 Estimated Fare: {fare:.2f} ETB\n\n"
            "🚖 Your ride request has been created successfully!"
        )

        # Clear the ride from memory
        del ride_requests[user_id]