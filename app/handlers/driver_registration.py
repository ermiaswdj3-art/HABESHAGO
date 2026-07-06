from telegram import Update
from telegram.ext import ContextTypes


from app.keyboards.toyota_models import (
    get_toyota_model_keyboard,
)
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
    text = update.message.text

    # ==========================================
    # PHONE NUMBER
    # ==========================================

    if state["step"] == "phone_number":

        state["phone_number"] = text
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

        # Toyota models
        if brand == "Toyota":

            await update.message.reply_text(
                "🚗 Please select your Toyota model.",
                reply_markup=get_toyota_model_keyboard(),
            )

        # Other brands (temporary)
        else:

            await update.message.reply_text(
                "🚘 Great!\n\n"
                "Please enter your vehicle model.\n\n"
                "Example:\n"
                "Vitz"
            )

        return

    # ==========================================
    # VEHICLE MODEL
    # ==========================================

    elif state["step"] == "vehicle_model":

        state["vehicle_model"] = text
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