from telegram import Update
from telegram.ext import ContextTypes

from app.constants.ride_status import (
    DRIVER_ARRIVED,
    TRIP_STARTED,
)

from app.database.driver_repository import (
    set_driver_available,
)

from app.database.ride_repository import (
    complete_ride,
    get_latest_driver_ride,
    get_ride_earnings,
    update_ride_status,
)

from app.keyboards.driver_menu import (
    get_driver_menu,
)

from app.keyboards.driver_ride_menu import (
    get_driver_ride_menu,
)

from app.keyboards.main_menu import (
    get_main_menu,
)

from app.keyboards.navigation import (
    get_destination_navigation_keyboard,
    get_pickup_navigation_keyboard,
)

from app.keyboards.rating_menu import (
    get_rating_menu,
)

from app.keyboards.trip_status import (
    get_trip_status_keyboard,
)

from app.services.distance_service import (
    calculate_distance,
)

from app.services.driver_service import (
    find_nearest_driver,
)

from app.services.eta_service import (
    calculate_eta,
)

from app.services.pricing_service import (
    calculate_fare,
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


async def confirm_ride(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Confirm the passenger's ride request and send it
    to the nearest available driver.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if user_id not in ride_requests:
        await update.message.reply_text(
            "❌ No active ride request found."
        )
        return

    pickup = ride_requests[user_id]["pickup"]
    destination = ride_requests[user_id]["destination"]

    if destination is None:
        await update.message.reply_text(
            "❌ Destination location is missing.\n\n"
            "Please request the ride again."
        )
        return

    # ==========================================
    # TRIP CALCULATIONS
    # ==========================================

    distance = calculate_distance(
        pickup[0],
        pickup[1],
        destination[0],
        destination[1],
    )

    fare = calculate_fare(distance)
    trip_eta = calculate_eta(distance)

    # ==========================================
    # FIND DRIVER
    # ==========================================

    driver = find_nearest_driver(
        pickup[0],
        pickup[1],
    )

    if driver is None:
        await update.message.reply_text(
            "😔 Sorry, we couldn't find an available driver nearby.\n\n"
            "Please try again in a few minutes.",
            reply_markup=get_main_menu(),
        )
        return

    pickup_eta = calculate_eta(
        driver["distance"]
    )

    # ==========================================
    # SAVE PENDING DRIVER REQUEST
    # ==========================================

    pending_driver_requests[driver["telegram_id"]] = {
        "passenger_id": user_id,
        "pickup": pickup,
        "destination": destination,
        "distance": distance,
        "pickup_distance": driver["distance"],
        "pickup_eta": pickup_eta,
        "trip_eta": trip_eta,
        "fare": fare,
        "payment_method": "Cash",
        "service_type": "fuel",
    }

    # ==========================================
    # SEND PROFESSIONAL RIDE CARD
    # ==========================================

    await context.bot.send_message(
        chat_id=driver["telegram_id"],
        text=(
            "🚖 NEW RIDE REQUEST\n\n"
            "🆔 Ride Reference: Pending\n\n"
            "📍 Pickup\n"
            f"{pickup[0]:.6f}, {pickup[1]:.6f}\n\n"
            "🏁 Destination\n"
            f"{destination[0]:.6f}, "
            f"{destination[1]:.6f}\n\n"
            "📏 Distance to Pickup\n"
            f"{driver['distance']:.2f} km\n\n"
            "⏱ Pickup ETA\n"
            f"{pickup_eta} minutes\n\n"
            "🛣 Trip Distance\n"
            f"{distance:.2f} km\n\n"
            "⏱ Estimated Trip\n"
            f"{trip_eta} minutes\n\n"
            "💰 Estimated Fare\n"
            f"{fare:.2f} ETB\n\n"
            "💳 Payment\n"
            "Cash"
        ),
        reply_markup=get_pickup_navigation_keyboard(
            pickup[0],
            pickup[1],
        ),
    )

    # Telegram cannot attach an inline keyboard and a reply
    # keyboard to the same message, so Accept/Decline is sent
    # as a second message.
    await context.bot.send_message(
        chat_id=driver["telegram_id"],
        text="Would you like to accept this ride?",
        reply_markup=get_driver_ride_menu(),
    )

    # ==========================================
    # NOTIFY PASSENGER
    # ==========================================

    await update.message.reply_text(
        "📡 Searching nearby drivers...\n\n"
        "🚖 A nearby driver has been found.\n\n"
        "⏳ Waiting for the driver's confirmation..."
    )


async def complete_ride_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Driver completes the ride.
    """

    if update.message is None:
        return

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

    # Mark ride completed.
    complete_ride(ride_id)

    # Retrieve the stored financial breakdown.
    earnings = get_ride_earnings(ride_id)

    # Driver becomes available again.
    set_driver_available(driver_id)

    # Remove active ride from memory.
    if driver_id in active_rides:
        del active_rides[driver_id]

    # Ask passenger to rate the driver.
    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "🎉 Your ride has been completed!\n\n"
            "⭐ Please rate your driver."
        ),
        reply_markup=get_rating_menu(),
    )

    # Fallback when financial information is unavailable.
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
        f"💵 Your Earnings: "
        f"{driver_earnings:.2f} ETB\n\n"
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

    if update.message is None:
        return

    user_id = update.effective_user.id

    if user_id in ride_requests:
        del ride_requests[user_id]

    # Remove pending driver requests belonging to this passenger.
    pending_driver_ids = [
        driver_id
        for driver_id, request in pending_driver_requests.items()
        if request.get("passenger_id") == user_id
    ]

    for driver_id in pending_driver_ids:
        del pending_driver_requests[driver_id]

    await update.message.reply_text(
        "❌ Your ride request has been cancelled.\n\n"
        "You can request another ride whenever you're ready.",
        reply_markup=get_main_menu(),
    )


async def arrived_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Driver has arrived at the passenger's pickup location.
    """

    if update.message is None:
        return

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

    # Notify passenger.
    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "📍 Your driver has arrived!\n\n"
            "🚶 Please proceed to the pickup point.\n\n"
            "👋 Your driver is waiting for you.\n\n"
            "We wish you a safe and pleasant trip "
            "with HABESHAGO 🇪🇹"
        ),
    )

    # Notify driver.
    await update.message.reply_text(
        "✅ Passenger has been notified.\n\n"
        "⏳ Please wait for the passenger to board.\n\n"
        "Once everyone is ready, tap 🚕 Start Trip.",
        reply_markup=get_trip_status_keyboard(),
    )


async def start_trip_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Driver starts the trip and receives navigation
    to the passenger's destination.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    if driver_id not in active_rides:
        await update.message.reply_text(
            "❌ You don't have an active ride."
        )
        return

    passenger_id = active_rides[driver_id]["passenger_id"]
    destination = active_rides[driver_id].get("destination")

    ride = get_latest_driver_ride(driver_id)

    if ride is not None:
        update_ride_status(
            ride[0],
            TRIP_STARTED,
        )

    # Notify passenger.
    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "🚕 Your trip has started!\n\n"
            "Enjoy your journey with HABESHAGO 🇪🇹"
        ),
    )

    # Fallback for older active-ride records that do not
    # contain destination coordinates.
    if destination is None:
        await update.message.reply_text(
            "🚕 Trip started successfully.\n\n"
            "Drive safely to the destination.\n\n"
            "When you reach the destination, "
            "tap 🏁 Complete Ride.",
            reply_markup=get_trip_status_keyboard(),
        )
        return

    # Send destination navigation as an inline button.
    await update.message.reply_text(
        "🚕 Trip started successfully!\n\n"
        "Use the button below to navigate "
        "to the destination.",
        reply_markup=get_destination_navigation_keyboard(
            destination[0],
            destination[1],
        ),
    )

    # Restore the normal ride-control keyboard.
    await update.message.reply_text(
        "Drive safely to the destination.\n\n"
        "When you reach the destination, "
        "tap 🏁 Complete Ride.",
        reply_markup=get_trip_status_keyboard(),
    )