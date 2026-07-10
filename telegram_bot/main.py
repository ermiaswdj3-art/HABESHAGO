import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config.settings import BOT_TOKEN
from app.database.database import create_tables

from app.handlers.start import start
from app.handlers.driver import become_driver
from app.handlers.driver_registration import (
    driver_registration_handler,
)
from app.handlers.driver_response import (
    accept_ride,
    decline_ride,
)
from app.handlers.ride import request_ride
from app.handlers.rides import show_rides
from app.handlers.profile import show_profile

from app.handlers.driver_dashboard import (
    show_driver_dashboard,
)

from app.handlers.set_phone import set_phone
from app.handlers.availability import (
    go_online,
    go_offline,
)
from app.handlers.location import receive_location
from app.handlers.rating import rate_driver_handler
from app.handlers.confirmation import (
    confirm_ride,
    cancel_ride,
    complete_ride_handler,
    arrived_handler,
    start_trip_handler,
)
from app.handlers.ride_status import (
    ride_status,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in .env")

    # Create database tables
    create_tables()

    # Create Telegram application
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rides", show_rides))
    app.add_handler(CommandHandler("profile", show_profile))
    app.add_handler(CommandHandler("driver", show_driver_dashboard))
    app.add_handler(CommandHandler("status", ride_status))
    app.add_handler(CommandHandler("setphone", set_phone))
    app.add_handler(CommandHandler("online", go_online))
    app.add_handler(CommandHandler("offline", go_offline))

    # Become Driver
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^💼 Become a Driver$"),
            become_driver,
        )
    )

    # Ride request
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🛺 Request Ride$"),
            request_ride,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📍 Ride Status$"),
            ride_status,
        )
    )
    # Confirm ride
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^✅ Confirm Ride$"),
            confirm_ride,
        )
    )

    # Cancel ride
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^❌ Cancel Ride$"),
            cancel_ride,
        )
    )

    # Driver arrived
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📍 Arrived$"),
            arrived_handler,
        )
    )   

    # Driver starts trip
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🚕 Start Trip$"),
            start_trip_handler,
        )
    )

    # Complete ride
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🏁 Complete Ride$"),
            complete_ride_handler,
        )
    )

    # Driver rating
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^⭐ [1-5]$"),
            rate_driver_handler,
        )
    )

    # Driver accepts ride
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^✅ Accept Ride$"),
            accept_ride,
        )
    )

    # Driver declines ride
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^❌ Decline Ride$"),
            decline_ride,
        )
    )

    # Driver goes online
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🟢 Go Online$"),
            go_online,
        )
    )

    # Driver goes offline
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🔴 Go Offline$"),
            go_offline,
        )
    )

    # Driver Dashboard
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🚖 Driver Dashboard$"),
            show_driver_dashboard,
        )
    )

    # Driver registration conversation
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.CONTACT) & ~filters.COMMAND,
            driver_registration_handler,
        )
    )
    # GPS location
    app.add_handler(
        MessageHandler(
            filters.LOCATION,
            receive_location,
        )
    )

    print("=" * 50)
    print("🚖 HABESHAGO Bot is running...")
    print("💾 Database initialized successfully.")
    print("Press Ctrl + C to stop the bot.")
    print("=" * 50)

    app.run_polling()


if __name__ == "__main__":
    main()