from telegram import Update
from telegram.ext import ContextTypes

from app.state.driver_state import pending_driver_requests
from app.state.ride_state import ride_requests
from app.database.driver_repository import (
    set_driver_unavailable,
    get_driver_by_id,
)
from app.database.ride_repository import save_ride
from app.keyboards.ride_menu import get_ride_menu


async def accept_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    driver_id = update.effective_user.id

    if driver_id not in pending_driver_requests:
        await update.message.reply_text(
            "❌ No pending ride request."
        )
        return

    request = pending_driver_requests[driver_id]

    save_ride(
        passenger_id=request["passenger_id"],
        driver_id=driver_id,
        pickup_latitude=request["pickup"][0],
        pickup_longitude=request["pickup"][1],
        destination_latitude=request["destination"][0],
        destination_longitude=request["destination"][1],
        distance=request["distance"],
        fare=request["fare"],
        status="Confirmed",
    )

    set_driver_unavailable(driver_id)
    driver = get_driver_by_id(driver_id)
    await context.bot.send_message(
        chat_id=request["passenger_id"],
        text=(
            "🎉 Your ride has been accepted!\n\n"
            f"👤 Driver: {driver[1]}\n"
            f"⭐ Rating: {driver[6]}\n"
            f"🚗 Vehicle: {driver[3]}\n"
            f"🎨 Color: {driver[4]}\n"
            f"🔢 Plate: {driver[5]}\n\n"
            "🚖 Your driver is on the way."
        ),
        reply_markup=get_ride_menu(),
    )

    await update.message.reply_text(
    "✅ Ride accepted successfully."
    )

    passenger_id = request["passenger_id"]

    if passenger_id in ride_requests:
        del ride_requests[passenger_id]

    del pending_driver_requests[driver_id]

   
async def decline_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    driver_id = update.effective_user.id

    if driver_id in pending_driver_requests:

        request = pending_driver_requests[driver_id]

        await context.bot.send_message(
            chat_id=request["passenger_id"],
            text=(
                "😔 Your driver declined the ride.\n\n"
                "Please request another ride."
            ),
        )

        del pending_driver_requests[driver_id]

    await update.message.reply_text(
        "❌ Ride declined."
    )