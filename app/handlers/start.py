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


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handle the /start command.

    - Registered drivers see the Driver Dashboard.
    - Everyone else is registered as a passenger.
    - Passengers see the main menu.
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

    # ==========================================
    # PASSENGER MAIN MENU
    # ==========================================

    await update.message.reply_text(
        "🚖 Welcome to HABESHAGO!\n\n"
        "Your trusted Ethiopian ride and delivery platform.\n\n"
        "Please choose an option below:",
        reply_markup=get_main_menu(),
    )