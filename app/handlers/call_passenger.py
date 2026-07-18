from telegram import (
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from app.database.passenger_repository import (
    get_passenger,
)

from app.state.active_ride_state import (
    active_rides,
)


async def call_passenger(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Share the assigned passenger's contact details
    with the driver during an active ride.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    # ==========================================
    # VERIFY ACTIVE RIDE
    # ==========================================

    if driver_id not in active_rides:
        await update.message.reply_text(
            "❌ You don't have an active ride."
        )
        return

    passenger_id = active_rides[driver_id]["passenger_id"]

    # ==========================================
    # GET PASSENGER PROFILE
    # ==========================================

    passenger = get_passenger(passenger_id)

    if passenger is None:
        await update.message.reply_text(
            "❌ Passenger profile could not be found."
        )
        return

    (
        telegram_id,
        full_name,
        phone_number,
        created_at,
    ) = passenger

    # Use the passenger's current Telegram name
    # when the stored database name is missing or invalid.
    clean_name = full_name.strip()

    if not clean_name or not any(
        character.isalnum()
        for character in clean_name
    ):
        try:
            passenger_chat = await context.bot.get_chat(
                passenger_id
            )

            name_parts = [
                passenger_chat.first_name,
                passenger_chat.last_name,
            ]

            full_name = " ".join(
                part
                for part in name_parts
                if part
            ).strip()

        except Exception:
            full_name = "Passenger"

    if not full_name:
        full_name = "Passenger"

    if not phone_number:
        await update.message.reply_text(
            "❌ The passenger has not provided a phone number."
        )
        return
    
    phone_number = phone_number.strip()

    if phone_number.startswith("00"):
        phone_number = f"+{phone_number[2:]}"

    elif phone_number.startswith("251"):
        phone_number = f"+{phone_number}"

    elif phone_number.startswith("0"):
        phone_number = f"+251{phone_number[1:]}"

    elif not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"

    # ==========================================
    # COPY-PHONE INLINE BUTTON
    # ==========================================

    copy_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📋 Copy Passenger Number",
                    copy_text=CopyTextButton(
                        text=phone_number,
                    ),
                ),
            ],
        ]
    )

    await update.message.reply_text(
        "📞 Passenger Contact\n\n"
        f"👤 Name: {full_name}\n"
        f"📱 Phone: {phone_number}\n\n"
        "Use the button below to copy the number, "
        "then paste it into your phone dialer.",
        reply_markup=copy_keyboard,
    )

    # ==========================================
    # SEND TELEGRAM CONTACT CARD
    # ==========================================

    await context.bot.send_contact(
        chat_id=driver_id,
        phone_number=phone_number,
        first_name=full_name,
    )