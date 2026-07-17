from telegram import Update
from telegram.ext import ContextTypes

from app.database.driver_repository import (
    get_driver_by_telegram_id,
)

from app.database.passenger_repository import (
    get_passenger,
    register_passenger,
)

from app.keyboards.driver_dashboard import (
    get_driver_dashboard_keyboard,
)

from app.keyboards.main_menu import (
    get_main_menu,
)

from app.keyboards.passenger_phone import (
    get_passenger_phone_keyboard,
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handle the /start command.

    - Registered drivers see the Driver Dashboard.
    - New passengers are registered automatically.
    - Passengers without a phone number are asked to share it.
    - Passengers with a saved phone number see the main menu.
    """

    user = update.effective_user
    user_id = user.id

    # ==========================================
    # DRIVER
    # ==========================================

    driver = get_driver_by_telegram_id(user_id)

    if driver is not None:
        await update.message.reply_text(
            "🚖 Welcome back, Driver!\n\n"
            "Your dashboard is ready.",
            reply_markup=get_driver_dashboard_keyboard(),
        )
        return

    # ==========================================
    # PASSENGER REGISTRATION
    # ==========================================

    register_passenger(
        telegram_id=user_id,
        full_name=user.full_name,
    )

    passenger = get_passenger(user_id)

    if passenger is None:
        await update.message.reply_text(
            "❌ We could not create your passenger profile.\n\n"
            "Please try /start again."
        )
        return

    phone_number = passenger[2]

    # ==========================================
    # PASSENGER PHONE NUMBER
    # ==========================================

    if not phone_number:
        context.user_data["awaiting_passenger_phone"] = True

        await update.message.reply_text(
            "🚖 Welcome to HABESHAGO!\n\n"
            "Before requesting your first ride, please share "
            "your phone number.\n\n"
            "Your number helps the driver contact you when necessary.",
            reply_markup=get_passenger_phone_keyboard(),
        )
        return

    # ==========================================
    # PASSENGER MAIN MENU
    # ==========================================

    context.user_data["awaiting_passenger_phone"] = False

    await update.message.reply_text(
        "🚖 Welcome back to HABESHAGO!\n\n"
        "Your trusted Ethiopian ride and delivery platform.\n\n"
        "Please choose an option below:",
        reply_markup=get_main_menu(),
    )