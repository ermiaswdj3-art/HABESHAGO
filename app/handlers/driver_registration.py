from telegram import Update
from telegram.ext import ContextTypes

from app.state.driver_registration_state import (
    driver_registration_state,
)
from app.keyboards.vehicle_color import (
    get_vehicle_color_keyboard,
)
from app.keyboards.plate_type import (
    get_plate_type_keyboard,
)

from app.keyboards.plate_region import (
    get_plate_region_keyboard,
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
            "Please choose your vehicle color.",
            reply_markup=get_vehicle_color_keyboard(),
        )

        return
    # ==========================================
    # VEHICLE COLOR
    # ==========================================

    elif state["step"] == "vehicle_color":

        color = (
            text.replace("⚪ ", "")
                .replace("⚫ ", "")
                .replace("🔘 ", "")
                .replace("⚙️ ", "")
                .replace("🔵 ", "")
                .replace("🔴 ", "")
                .replace("🟢 ", "")
                .replace("🟡 ", "")
                .replace("🟤 ", "")
                .replace("🟣 ", "")
                .replace("🟠 ", "")
                .replace("🚗 ", "")
        )

        state["vehicle_color"] = color

        state["step"] = "plate_type"

        await update.message.reply_text(
            "🚘 Please choose your plate type.",
            reply_markup=get_plate_type_keyboard(),
        )

        return

    # ==========================================
    # PLATE TYPE
    # ==========================================

    elif state["step"] == "plate_type":

        state["plate_type"] = text

        if text == "🟦 Regional Plate":

            state["step"] = "plate_region"

            await update.message.reply_text(
            "🇪🇹 Please select your regional plate code.",
            reply_markup=get_plate_region_keyboard(),
            )

        elif text == "🟩 National ETH Plate":

            state["step"] = "eth_letters"

            await update.message.reply_text(
                "🔤 Please enter the three letters.\n\n"
                "Example:\n"
                "ABC"
            )

        return

    # ==========================================
    # REGIONAL PLATE
    # ==========================================

    elif state["step"] == "plate_region":

        state["plate_region"] = text
        state["step"] = "plate_number"

        await update.message.reply_text(
            "🔢 Please enter the plate number.\n\n"
            "Example:\n"
            "12345"
        )

        return
    
    # ==========================================
    # ETH LETTERS
    # ==========================================

    elif state["step"] == "eth_letters":

        letters = text.upper().strip()

        if len(letters) != 3 or not letters.isalpha():

            await update.message.reply_text(
                "❌ Please enter exactly 3 letters.\n\n"
                "Example:\n"
                "ABC"
            )

            return

        state["eth_letters"] = letters
        state["step"] = "eth_numbers"

        await update.message.reply_text(
            "🔢 Please enter the four digits.\n\n"
            "Example:\n"
            "1234"
        )

        return

    # ==========================================
    # ETH NUMBERS
    # ==========================================

    elif state["step"] == "eth_numbers":

        numbers = text.strip()

        if len(numbers) != 4 or not numbers.isdigit():

            await update.message.reply_text(
                "❌ Please enter exactly 4 digits.\n\n"
                "Example:\n"
                "1234"
            )

            return

        state["plate_number"] = (
            f'ETH {state["eth_letters"]} {numbers}'
        )

        state["step"] = "location"

        await update.message.reply_text(
            "📍 Perfect!\n\n"
            "Please share your current location.\n\n"
            "This location will be used to match you with nearby passengers.",
            reply_markup=get_driver_location_keyboard(),
        )

        return


    # ==========================================
    # PLATE NUMBER
    # ==========================================

    elif state["step"] == "plate_number":

        # Regional Plate
        if state.get("plate_type") == "🟦 Regional Plate":

            state["plate_number"] = (
                f'{state["plate_region"]}-{text}'
            )

        # National ETH Plate (temporary)
        else:

            state["plate_number"] = text

        state["step"] = "location"

        await update.message.reply_text(
            "📍 Perfect!\n\n"
            "Please share your current location.\n\n"
            "This location will be used to match you with nearby passengers.",
            reply_markup=get_driver_location_keyboard(),
        )

        return