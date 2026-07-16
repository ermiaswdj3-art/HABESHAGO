from telegram import Update
from telegram.ext import ContextTypes

from app.database.driver_repository import (
    update_driver_location,
)


async def update_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Receive a driver's live location and update it in the database.
    """

    if update.message.location is None:
        return

    driver_id = update.effective_user.id

    latitude = update.message.location.latitude
    longitude = update.message.location.longitude

    update_driver_location(
        driver_id,
        latitude,
        longitude,
    )

    await update.message.reply_text(
        "📍 Location updated successfully!\n\n"
        "Passengers will now find you using your latest location."
    )