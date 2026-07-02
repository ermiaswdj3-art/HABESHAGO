from telegram import Update
from telegram.ext import ContextTypes

from app.database.ride_repository import get_rides_by_passenger


async def show_rides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    rides = get_rides_by_passenger(user_id)

    if not rides:
        await update.message.reply_text(
            "📭 You don't have any ride history yet."
        )
        return

    message = "📜 Your Ride History\n\n"

    for index, ride in enumerate(rides, start=1):
        distance, fare, status = ride

        message += (
            f"{index}.\n"
            f"📏 Distance: {distance:.2f} km\n"
            f"💰 Fare: {fare:.2f} ETB\n"
            f"📌 Status: {status}\n\n"
        )

    await update.message.reply_text(message)