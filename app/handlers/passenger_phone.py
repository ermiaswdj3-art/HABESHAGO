from telegram import Update
from telegram.ext import ContextTypes

from app.database.passenger_repository import (
    get_passenger,
    update_passenger_contact,
)

from app.keyboards.main_menu import (
    get_main_menu,
)


async def save_passenger_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Save a passenger's shared Telegram phone number.
    """

    if update.message is None or update.message.contact is None:
        return

    user_id = update.effective_user.id
    contact = update.message.contact

    # Prevent users from submitting another person's contact.
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
        context.user_data["awaiting_passenger_phone"] = False

        await update.message.reply_text(
            "❌ Passenger profile not found.\n\n"
            "Please use /start and try again."
        )
        return

    contact_name = " ".join(
        part
        for part in [
          contact.first_name,
          contact.last_name,
        ]
        if part
    ).strip()

    if not contact_name:
        contact_name = update.effective_user.full_name

    update_passenger_contact(
        telegram_id=user_id,
        full_name=contact_name,
        phone_number=contact.phone_number,
    )

    context.user_data["awaiting_passenger_phone"] = False

    await update.message.reply_text(
        "✅ Your phone number has been saved successfully!\n\n"
        "You can now request rides and use the passenger services.",
        reply_markup=get_main_menu(),
    )