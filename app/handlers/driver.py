from telegram import Update
from telegram.ext import ContextTypes

from app.state.driver_registration_state import driver_registration_state
from app.keyboards.contact import get_contact_keyboard
from app.keyboards.driver_location import get_driver_location_keyboard
from app.keyboards.availability import (
    get_availability_keyboard,
)


async def become_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start the Driver Registration Wizard.
    """

    user_id = update.effective_user.id

    driver_registration_state[user_id] = {
        "step": "phone_number"
    }

    await update.message.reply_text(
        "🚖 Welcome to HABESHAGO Driver Registration!\n\n"
        "Let's get you registered.\n\n"
        "📱 Tap the button below to securely share your phone number.",
        reply_markup=get_contact_keyboard(),
    )


async def driver_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle every step of the Driver Registration Wizard.
    """

    user_id = update.effective_user.id

    if user_id not in driver_registration_state:
        return

    state = driver_registration_state[user_id]
    text = update.message.text

    # ==========================================
    # PHONE NUMBER
    # ==========================================

    if state["step"] == "phone_number":

        state["phone_number"] = text
        state["step"] = "vehicle"

        await update.message.reply_text(
            "🚗 Great!\n\n"
            "Please enter your vehicle model.\n\n"
            "Example:\n"
            "Toyota Vitz"
        )

        return

    # ==========================================
    # VEHICLE
    # ==========================================

    if state["step"] == "vehicle":

        state["vehicle"] = text
        state["step"] = "vehicle_color"

        await update.message.reply_text(
            "🎨 Great!\n\n"
            "Please enter your vehicle color.\n\n"
            "Example:\n"
            "White"
        )

        return

    # ==========================================
    # VEHICLE COLOR
    # ==========================================

    if state["step"] == "vehicle_color":

        state["vehicle_color"] = text
        state["step"] = "plate_number"

        await update.message.reply_text(
            "🔢 Excellent!\n\n"
            "Please enter your plate number.\n\n"
            "Example:\n"
            "AA-12345"
        )

        return

    # ==========================================
    # PLATE NUMBER
    # ==========================================

    if state["step"] == "plate_number":

        state["plate_number"] = text
        state["step"] = "location"

        await update.message.reply_text(
            "📍 Perfect!\n\n"
            "Please share your current location.\n\n"
            "This location will be used to match you with nearby passengers.",
            reply_markup=get_driver_location_keyboard(),
        )

        return