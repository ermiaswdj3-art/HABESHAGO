from telegram import Update
from telegram.ext import ContextTypes

from app.database.ride_repository import save_ride
from app.services.driver_service import find_nearest_driver
from app.services.distance_service import calculate_distance
from app.services.pricing_service import calculate_fare
from app.state.ride_state import ride_requests


async def confirm_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ride_requests:
        await update.message.reply_text(
            "❌ No active ride request found."
        )
        return

    pickup = ride_requests[user_id]["pickup"]
    destination = ride_requests[user_id]["destination"]

    distance = calculate_distance(
        pickup[0],
        pickup[1],
        destination[0],
        destination[1],
    )

    fare = calculate_fare(distance)

    driver = find_nearest_driver(
        pickup[0],
        pickup[1],
    )

    if driver is None:
        await update.message.reply_text(
            "😔 Sorry, no drivers are currently available."
        )
        return

    # Save ride to the database
    save_ride(
        passenger_id=user_id,
        pickup_latitude=pickup[0],
        pickup_longitude=pickup[1],
        destination_latitude=destination[0],
        destination_longitude=destination[1],
        distance=distance,
        fare=fare,
        status="Confirmed",
    )

    await update.message.reply_text(
        "✅ Your ride has been confirmed!\n\n"
        "🚖 Driver Found!\n\n"
        f"👤 Driver: {driver['name']}\n"
        f"⭐ Rating: {driver['rating']}\n"
        f"🚗 Vehicle: {driver['vehicle']}\n"
        f"🎨 Color: {driver['color']}\n"
        f"🔢 Plate: {driver['plate']}\n\n"
        "💾 Ride saved successfully.\n\n"
        "🚗 Your driver is on the way."
    )

    del ride_requests[user_id]


async def cancel_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in ride_requests:
        del ride_requests[user_id]

    await update.message.reply_text(
        "❌ Your ride request has been cancelled."
    )