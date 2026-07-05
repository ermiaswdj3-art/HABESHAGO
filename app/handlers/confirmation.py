from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.ride_menu import get_ride_menu
from app.keyboards.rating_menu import get_rating_menu
from app.state.driver_state import pending_driver_requests
from app.keyboards.driver_ride_menu import get_driver_ride_menu

from app.database.driver_repository import (
    set_driver_unavailable,
    set_driver_available,
)

from app.database.ride_repository import (
    save_ride,
    get_latest_confirmed_ride,
    complete_ride,
)

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

    pending_driver_requests[driver["telegram_id"]] = {
        "passenger_id": user_id,
        "pickup": pickup,
        "destination": destination,
        "distance": distance,
        "fare": fare,
    }

    await context.bot.send_message(
        chat_id=driver["telegram_id"],
        text=(
            "🚖 New Ride Request!\n\n"
            f"📍 Pickup: {pickup}\n"
            f"🏁 Destination: {destination}\n"
            f"📏 Distance: {distance:.2f} km\n"
            f"💰 Fare: {fare:.2f} ETB\n\n"
            "Would you like to accept this ride?"
        ),
        reply_markup=get_driver_ride_menu(),
    )

    await update.message.reply_text(
        "📡 Ride request sent to the nearest driver.\n\n"
        "⏳ Waiting for driver response..."
    )



async def complete_ride_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    print("========== COMPLETE RIDE ==========")
    print("STEP 1: Button pressed")
    print("Passenger ID:", user_id)

    ride = get_latest_confirmed_ride(user_id)

    print("STEP 2: Ride found ->", ride)

    if ride is None:
        await update.message.reply_text(
            "❌ You don't have an active ride."
        )
        return

    ride_id = ride[0]
    driver_id = ride[1]

    print("Ride ID:", ride_id)
    print("Driver ID:", driver_id)

    complete_ride(ride_id)

    print("STEP 3: Ride marked as Completed")

    set_driver_available(driver_id)

    print("STEP 4: Driver marked Available")

    await update.message.reply_text(
        "🎉 Ride completed successfully!\n\n"
        "✅ Driver is now available for new passengers.\n\n"
        "⭐ Please rate your driver.",
        reply_markup=get_rating_menu(),
    )

    print("STEP 5: Rating keyboard sent")


async def cancel_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in ride_requests:
        del ride_requests[user_id]

    await update.message.reply_text(
        "❌ Your ride request has been cancelled."
    )