from telegram import Update
from telegram.ext import ContextTypes

from app.database.passenger_repository import (
    get_passenger,
    update_phone_number,
)

from app.keyboards.main_menu import get_main_menu


async def save_passenger_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Save a passenger's shared phone number.
    """

    if update.message is None or update.message.contact is None:
        return

    user_id = update.effective_user.id
    contact = update.message.contact

    # Prevent a user from submitting someone else's contact.
    if (
        contact.user_id is not None
        and contact.user_id != user_id
    ):
        await update.message.reply_text(
            "❌ Please share your own phone number."
        )
        return

    passenger = get_passenger(user_id)

    if passenger is None:
        await update.message.reply_text(
            "❌ Passenger profile not found.\n\n"
            "Please use /start first."
        )
        return

    update_phone_number(
        telegram_id=user_id,
        phone_number=contact.phone_number,
    )

    await update.message.reply_text(
        "✅ Your phone number has been saved successfully!",
        reply_markup=get_main_menu(),
    )