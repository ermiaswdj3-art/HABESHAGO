from telegram import Update
from telegram.ext import ContextTypes

from app.state.ride_state import ride_requests


async def receive_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    location = update.message.location

    latitude = location.latitude
    longitude = location.longitude

    # New ride request
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
            "📍 Now please send your destination location."
        )

    # Destination received
    else:
        ride_requests[user_id]["destination"] = (latitude, longitude)
        ride_requests[user_id]["status"] = "completed"

        pickup = ride_requests[user_id]["pickup"]
        destination = ride_requests[user_id]["destination"]

        await update.message.reply_text(
            "🎉 Ride request completed!\n\n"
            f"📍 Pickup:\n"
            f"Latitude: {pickup[0]}\n"
            f"Longitude: {pickup[1]}\n\n"
            f"🏁 Destination:\n"
            f"Latitude: {destination[0]}\n"
            f"Longitude: {destination[1]}\n\n"
            "🚖 Your ride request has been created successfully!"
        )