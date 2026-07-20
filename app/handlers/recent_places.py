from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from app.database.passenger_places_repository import (
    get_recent_places,
)

from app.state.ride_state import (
    ride_requests,
)


async def show_recent_places(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Show the passenger's latest saved destinations.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if (
        user_id not in ride_requests
        or ride_requests[user_id].get("status")
        != "waiting_for_destination"
    ):
        await update.message.reply_text(
            "❌ Please share your pickup location first."
        )
        return

    recent_places = get_recent_places(
        user_id,
        limit=5,
    )

    if not recent_places:
        await update.message.reply_text(
            "🕒 You don't have any recent places yet.\n\n"
            "Search for a destination or share its location first."
        )
        return

    context.user_data["recent_places"] = recent_places

    keyboard = []

    for index, place in enumerate(
        recent_places,
        start=1,
    ):
        place_name = place[1]

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{index}. 📍 {place_name}",
                    callback_data=f"recent_place:{index - 1}",
                )
            ]
        )

    await update.message.reply_text(
        "🕒 Recent Places\n\n"
        "Choose a destination:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
    )