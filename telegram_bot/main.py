import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config.settings import BOT_TOKEN
from app.handlers.start import start
from app.handlers.ride import request_ride
from app.handlers.location import receive_location

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    # Check if BOT_TOKEN exists
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in .env")

    # Create the Telegram application
    app = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))

    # Register message handlers
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^🛺 Request Ride$"),
            request_ride,
        )
    )

    # Handle location messages
    app.add_handler(
        MessageHandler(
            filters.LOCATION,
            receive_location,
        )
    )

    print("=" * 50)
    print("🚖 HABESHAGO Bot is running...")
    print("Press Ctrl + C to stop the bot.")
    print("=" * 50)

    # Start the bot
    app.run_polling()


if __name__ == "__main__":
    main()