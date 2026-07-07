from telegram import Update
from telegram.ext import ContextTypes

from app.state.driver_registration_state import (
    driver_registration_state,
)

from app.keyboards.vehicle_type import (
    get_vehicle_type_keyboard,
)

from app.keyboards.vehicle_brand import (
    get_vehicle_brand_keyboard,
)

from app.keyboards.electric_vehicle_brand import (
    get_electric_vehicle_brand_keyboard,
)

from app.keyboards.motorcycle_brand import (
    get_motorcycle_brand_keyboard,
)

from app.keyboards.model_keyboard import (
    get_vehicle_model_keyboard,
)

from app.keyboards.driver_location import (
    get_driver_location_keyboard,
)
from app.keyboards.vehicle_year import (
    get_vehicle_year_keyboard,
)

async def driver_registration_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    if user_id not in driver_registration_state:
        return

    state = driver_registration_state[user_id]
    text = update.message.text if update.message.text else ""

    # ==========================================
    # PHONE NUMBER
    # ==========================================

    if state["step"] == "phone_number":

        # Driver didn't share a contact
        if update.message.contact is None:

            await update.message.reply_text(
                "📱 Please use the button below to share your phone number."
            )

            return

        # Save the phone number from Telegram
        state["phone_number"] = update.message.contact.phone_number
        state["step"] = "vehicle_type"

        await update.message.reply_text(
            "🚘 Please choose your vehicle type.",
            reply_markup=get_vehicle_type_keyboard(),
        )

        return

    # ==========================================
    # VEHICLE TYPE
    # ==========================================

    elif state["step"] == "vehicle_type":

        state["vehicle_type"] = text
        state["step"] = "vehicle"

        if text == "⛽ Fuel Car":

            await update.message.reply_text(
                "🚗 Please select your vehicle brand.",
                reply_markup=get_vehicle_brand_keyboard(),
            )

        elif text == "⚡ Electric Car":

            await update.message.reply_text(
                "⚡ Please select your electric vehicle brand.",
                reply_markup=get_electric_vehicle_brand_keyboard(),
            )

        elif text == "🏍 Motorcycle":

            await update.message.reply_text(
                "🏍 Please select your motorcycle brand.",
                reply_markup=get_motorcycle_brand_keyboard(),
            )

        return

    # ==========================================
    # VEHICLE BRAND
    # ==========================================

    elif state["step"] == "vehicle":

        brand = (
            text.replace("🚗 ", "")
                .replace("⚡ ", "")
                .replace("🏍 ", "")
        )

        state["vehicle_brand"] = brand
        state["step"] = "vehicle_model"

        vehicle_type = (
            state["vehicle_type"]
                .replace("⛽ ", "")
                .replace("⚡ ", "")
                .replace("🏍 ", "")
        )

        await update.message.reply_text(
            f"🚘 Please select your {brand} model.",
            reply_markup=get_vehicle_model_keyboard(
                vehicle_type,
                brand,
            ),
        )

        return

    # ==========================================
    # VEHICLE MODEL
    # ==========================================

    elif state["step"] == "vehicle_model":

        # Driver selected "Other"
        if text == "Other":

            state["step"] = "custom_vehicle_model"

            await update.message.reply_text(
                f"✍ Please type your {state['vehicle_brand']} model."
            )

            return

        # Driver selected a predefined model
        state["vehicle_model"] = text
        state["step"] = "vehicle_year"

        await update.message.reply_text(
            "📅 Please select your vehicle's manufacturing year.",
            reply_markup=get_vehicle_year_keyboard(),
        )

        return
    
    # ==========================================
    # CUSTOM VEHICLE MODEL
    # ==========================================

    elif state["step"] == "custom_vehicle_model":

        state["vehicle_model"] = text
        state["step"] = "vehicle_year"

        await update.message.reply_text(
            "📅 Please select your vehicle's manufacturing year.",
            reply_markup=get_vehicle_year_keyboard(),
        )

        return
    # ==========================================
    # VEHICLE YEAR
    # ==========================================

    elif state["step"] == "vehicle_year":

        state["vehicle_year"] = text
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

    elif state["step"] == "vehicle_color":

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

    elif state["step"] == "plate_number":

        state["plate_number"] = text
        state["step"] = "location"

        await update.message.reply_text(
            "📍 Perfect!\n\n"
            "Please share your current location.\n\n"
            "This location will be used to match you with nearby passengers.",
            reply_markup=get_driver_location_keyboard(),
        )

        return