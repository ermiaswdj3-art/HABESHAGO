from telegram import Update
from telegram.ext import ContextTypes

from app.state.driver_registration_state import (
    driver_registration_state,
)
from app.keyboards.driver_location import (
    get_driver_location_keyboard,
)


async def driver_registration_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    if user_id not in driver_registration_state:
        return

    state = driver_registration_state[user_id]

    if state["step"] == "phone_number":

        state["phone_number"] = update.message.text
        state["step"] = "vehicle"

        await update.message.reply_text(
            "🚗 Great!\n\n"
            "Please enter your vehicle model.\n\n"
            "Example:\n"
            "Toyota Vitz"
        )

    elif state["step"] == "vehicle":

        state["vehicle"] = update.message.text
        state["step"] = "vehicle_color"

        await update.message.reply_text(
            "🎨 Great!\n\n"
            "Please enter your vehicle color.\n\n"
            "Example:\n"
            "White"
        )

    elif state["step"] == "vehicle_color":

        state["vehicle_color"] = update.message.text
        state["step"] = "plate_number"

        await update.message.reply_text(
            "🔢 Excellent!\n\n"
            "Please enter your plate number.\n\n"
            "Example:\n"
            "AA-12345"
        )

    elif state["step"] == "plate_number":

        state["plate_number"] = update.message.text
        state["step"] = "location"

        await update.message.reply_text(
            "📍 Perfect!\n\n"
            "Please share your current location.\n\n"
            "This location will be used to match you with nearby passengers.",
            reply_markup=get_driver_location_keyboard(),
        )