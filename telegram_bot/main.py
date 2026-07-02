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
from app.handlers.ride import request_ride
from app.handlers.location import receive_location
from app.handlers.confirmation import (
    confirm_ride,
    cancel_ride,
)
from app.handlers.rides import show_rides

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in .env")

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rides", show_rides))

    # Ride request
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🛺 Request Ride$"),
            request_ride,
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