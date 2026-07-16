from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.location import get_location_keyboard


async def request_driver_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Ask the driver to share their current location.
    """

    context.user_data["driver_update_location"] = True

    await update.message.reply_text(
        "📍 Please share your current location.",
        reply_markup=get_location_keyboard(
            "📍 Share Current Location"
        ),
    )