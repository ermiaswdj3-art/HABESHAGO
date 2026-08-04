"""
HABESHAGO Start Handler

Routes each Telegram user according to their current
HABESHAGO role and driver verification status.
"""

from telegram import Update
from telegram.ext import ContextTypes

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

from app.services.driver_registration_service import (
    get_driver_registration_status,
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handle the /start command.

    - Approved drivers see the Driver Dashboard.
    - Pending, rejected, or suspended driver applicants
      see their registration status.
    - New passengers are registered automatically.
    - Passengers without a phone number are asked to share it.
    - Passengers with a saved phone number see the main menu.
    """

    if update.message is None:
        return

    user = update.effective_user
    user_id = user.id

    # ==========================================
    # DRIVER REGISTRATION STATUS
    # ==========================================

    driver_status = get_driver_registration_status(
        user_id
    )

    if driver_status is not None:
        registration = driver_status[
            "registration"
        ]

        verification = driver_status[
            "verification"
        ]

        guidance = driver_status[
            "guidance"
        ]

        if driver_status["can_operate"]:
            await update.message.reply_text(
                "🚖 Welcome back, Driver!\n\n"
                "Your verified HABESHAGO Driver "
                "Dashboard is ready.",
                reply_markup=(
                    get_driver_dashboard_keyboard()
                ),
            )
            return

        rejection_reason = registration.get(
            "rejection_reason"
        )

        rejection_section = ""

        if rejection_reason:
            rejection_section = (
                "\n\nReason\n"
                f"{rejection_reason}"
            )

        await update.message.reply_text(
            "🚖 HABESHAGO DRIVER APPLICATION\n\n"

            "Registration Status\n"
            f"{registration['label']}\n\n"

            "Identity Verification\n"
            f"{verification['identity'].replace('_', ' ').title()}\n\n"

            "Vehicle Verification\n"
            f"{verification['vehicle'].replace('_', ' ').title()}\n\n"

            f"{guidance['message']}\n\n"

            "Next Action\n"
            f"{guidance['next_action']}"

            f"{rejection_section}"
        )
        return

    # ==========================================
    # PASSENGER REGISTRATION
    # ==========================================

    register_passenger(
        telegram_id=user_id,
        full_name=user.full_name,
    )

    passenger = get_passenger(
        user_id
    )

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
        context.user_data[
            "awaiting_passenger_phone"
        ] = True

        await update.message.reply_text(
            "🚖 Welcome to HABESHAGO!\n\n"
            "Before requesting your first ride, "
            "please share your phone number.\n\n"
            "Your number helps the driver contact "
            "you when necessary.",
            reply_markup=(
                get_passenger_phone_keyboard()
            ),
        )
        return

    # ==========================================
    # PASSENGER MAIN MENU
    # ==========================================

    context.user_data[
        "awaiting_passenger_phone"
    ] = False

    await update.message.reply_text(
        "🚖 Welcome back to HABESHAGO!\n\n"
        "Your trusted Ethiopian ride and "
        "delivery platform.\n\n"
        "Please choose an option below:",
        reply_markup=get_main_menu(),
    )