from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.driver_menu import get_driver_menu
from app.keyboards.rating_menu import get_rating_menu
from app.keyboards.main_menu import (
    get_main_menu,
)
from app.state.driver_state import pending_driver_requests
from app.state.active_ride_state import active_rides

from app.database.ride_repository import (
    update_ride_status,
)
from app.keyboards.driver_ride_menu import get_driver_ride_menu

from app.keyboards.trip_status import (
    get_trip_status_keyboard,
)

from app.database.driver_repository import (
    set_driver_available,
)

from app.constants.ride_status import (
    DRIVER_ARRIVED,
    TRIP_STARTED,
)

from app.database.ride_repository import (
    get_latest_driver_ride,
    complete_ride,
    get_ride_earnings,
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
            "😔 Sorry, we couldn't find an available driver nearby.\n\n"
            "Please try again in a few minutes."
        )
        return

    pending_driver_requests[driver["telegram_id"]] = {
        "passenger_id": user_id,
        "pickup": pickup,
        "destination": destination,
        "distance": distance,
        "pickup_distance": driver["distance"],
        "fare": fare,
    }

    await context.bot.send_message(
        chat_id=driver["telegram_id"],
        text=(
            "🚖 New Ride Request!\n\n"
            f"📍 Pickup: {pickup}\n"
            f"🏁 Destination: {destination}\n"
            f"📍 Pickup Distance: {driver['distance']:.2f} km\n"
            f"🛣 Trip Distance: {distance:.2f} km\n"
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
    """
    Driver completes the ride.
    """

    driver_id = update.effective_user.id

    print("========== COMPLETE RIDE ==========")
    print("Driver ID:", driver_id)

    ride = get_latest_driver_ride(driver_id)

    print("Ride found:", ride)

    if ride is None:

        await update.message.reply_text(
            "❌ You don't have an active ride."
        )

        return

    ride_id = ride[0]
    passenger_id = ride[1]

    # Mark ride completed
    complete_ride(ride_id)
    earnings = get_ride_earnings(ride_id)

    # Driver becomes available again
    set_driver_available(driver_id)

    # Remove active ride from memory
    if driver_id in active_rides:
        del active_rides[driver_id]

    # Ask passenger to rate driver
    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "🎉 Your ride has been completed!\n\n"
            "⭐ Please rate your driver."
        ),
        reply_markup=get_rating_menu(),
    )

    # Notify driver
    if earnings is None:
        await update.message.reply_text(
            "✅ Ride completed successfully!\n\n"
            "🟢 You are now available for new ride requests.",
            reply_markup=get_driver_menu(),
        )
        return

    (
        fare,
        service_type,
        commission_rate,
        commission_amount,
        driver_earnings,
    ) = earnings

    commission_percentage = int(
        commission_rate * 100
    )

    service_names = {
        "fuel": "⛽ Fuel Ride",
        "ev": "⚡ EV Ride",
        "premium": "👑 Premium Ride",
        "delivery": "🛵 Delivery",
    }

    display_service = service_names.get(
        service_type,
        service_type.title(),
    )

    await update.message.reply_text(
        "✅ Ride completed successfully!\n\n"
        f"🚖 Service: {display_service}\n"
        f"💰 Ride Fare: {fare:.2f} ETB\n"
        f"📉 HABESHAGO Commission "
        f"({commission_percentage}%): "
        f"{commission_amount:.2f} ETB\n"
        f"💵 Your Earnings: {driver_earnings:.2f} ETB\n\n"
        "🟢 You are now available for new ride requests.",
        reply_markup=get_driver_menu(),
    )


async def cancel_ride(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Cancel the passenger's current ride request
    and restore the passenger main menu.
    """

    user_id = update.effective_user.id

    if user_id in ride_requests:
        del ride_requests[user_id]

    await update.message.reply_text(
        "❌ Your ride request has been cancelled.\n\n"
        "You can request another ride whenever you're ready.",
        reply_markup=get_main_menu(),
    )

async def arrived_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Driver has arrived at the passenger's pickup location.
    """

    driver_id = update.effective_user.id

    if driver_id not in active_rides:

        await update.message.reply_text(
            "❌ You don't have an active ride."
        )

        return

    passenger_id = active_rides[driver_id]["passenger_id"]

    ride = get_latest_driver_ride(driver_id)

    if ride is not None:
        update_ride_status(
            ride[0],
            DRIVER_ARRIVED,
        )

    # Notify passenger
    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "📍 Your driver has arrived!\n\n"
            "🚶 Please proceed to the pickup point.\n\n"
            "👋 Your driver is waiting for you.\n\n"
            "We wish you a safe and pleasant trip with HABESHAGO 🇪🇹"
        ),
    )

    # Notify driver
    await update.message.reply_text(
        "✅ Passenger has been notified.\n\n"
        "⏳ Please wait for the passenger to board.\n\n"
        "Once everyone is ready, tap 🚕 Start Trip.",
        reply_markup=get_trip_status_keyboard(),
    )
    
async def start_trip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Driver starts the trip.
    """

    driver_id = update.effective_user.id

    if driver_id not in active_rides:

        await update.message.reply_text(
            "❌ You don't have an active ride."
        )

        return

    passenger_id = active_rides[driver_id]["passenger_id"]
    ride = get_latest_driver_ride(driver_id)

    if ride is not None:
        update_ride_status(
            ride[0],
            TRIP_STARTED,
        )

    # Notify passenger
    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "🚕 Your trip has started!\n\n"
            "Enjoy your journey with HABESHAGO 🇪🇹"
        ),
    )

    # Notify driver
    await update.message.reply_text(
        "🚕 Trip started successfully.\n\n"
        "Drive safely to the destination.\n\n"
        "When you reach the destination, tap 🏁 Complete Ride.",
        reply_markup=get_trip_status_keyboard(),
    )