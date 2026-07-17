from telegram import Update
from telegram.ext import ContextTypes

from app.state.driver_registration_state import (
    driver_registration_state,
)

from app.handlers.driver_registration import (
    driver_registration_handler,
)

from app.handlers.passenger_phone import (
    save_passenger_phone,
)


async def route_contact(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Route a shared Telegram contact to the correct workflow.

    - Driver registration contact
    - Passenger phone-number contact
    """

    if update.message is None or update.message.contact is None:
        return

    user_id = update.effective_user.id

    # ==========================================
    # DRIVER REGISTRATION CONTACT
    # ==========================================

    if user_id in driver_registration_state:
        await driver_registration_handler(
            update,
            context,
        )
        return

    # ==========================================
    # PASSENGER PHONE CONTACT
    # ==========================================

    if context.user_data.get("awaiting_passenger_phone") is True:
        await save_passenger_phone(
            update,
            context,
        )
        return

    # ==========================================
    # UNKNOWN CONTACT
    # ==========================================

    await update.message.reply_text(
        "❌ I wasn't expecting a phone number right now.\n\n"
        "Please use /start and choose the appropriate option."
    )