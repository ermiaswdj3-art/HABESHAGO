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
from app.handlers.contact_router import (
    route_contact,
)
from app.handlers.update_driver_location import (
    request_driver_location,
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


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in .env")

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()

    # ==========================================
    # COMMANDS
    # ==========================================

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rides", show_rides))
    app.add_handler(CommandHandler("profile", show_profile))
    app.add_handler(CommandHandler("driver", show_driver_dashboard))
    app.add_handler(CommandHandler("status", ride_status))
    app.add_handler(CommandHandler("setphone", set_phone))
    app.add_handler(CommandHandler("online", go_online))
    app.add_handler(CommandHandler("offline", go_offline))

    # ==========================================
    # PASSENGER MENU
    # ==========================================

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

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^✅ Confirm Ride$"),
            confirm_ride,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^❌ Cancel Ride$"),
            cancel_ride,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^👤 My Profile$"),
            show_profile,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📋 My Rides$"),
            show_rides,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^💼 Register as Driver$"),
            become_driver,
        )
    )

    # ==========================================
    # DRIVER RIDE FLOW
    # ==========================================

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^✅ Accept Ride$"),
            accept_ride,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^❌ Decline Ride$"),
            decline_ride,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📍 Arrived$"),
            arrived_handler,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🚕 Start Trip$"),
            start_trip_handler,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🏁 Complete Ride$"),
            complete_ride_handler,
        )
    )

    # ==========================================
    # DRIVER DASHBOARD
    # ==========================================

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🚖 Driver Dashboard$"),
            show_driver_dashboard,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🟢 Go Online$"),
            go_online,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🔴 Go Offline$"),
            go_offline,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^📍 Update My Location$"),
            request_driver_location,
        )
    )

    # ==========================================
    # RATINGS
    # ==========================================

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^⭐ [1-5]$"),
            rate_driver_handler,
        )
    )

    # ==========================================
    # CONTACT ROUTING
    # ==========================================

    app.add_handler(
        MessageHandler(
            filters.CONTACT,
            route_contact,
        )
    )

    # ==========================================
    # DRIVER REGISTRATION TEXT FLOW
    # ==========================================

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            driver_registration_handler,
        )
    )

    # ==========================================
    # LOCATION ROUTING
    # ==========================================

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