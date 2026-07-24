from telegram import Update
from telegram.ext import ContextTypes

from app.database.driver_repository import (
    update_driver_rating,
)

from app.database.ride_repository import (
    get_latest_completed_ride,
    rate_driver,
)

from app.keyboards.main_menu import (
    get_main_menu,
)

from app.services.idempotency_service import (
    is_duplicate_action,
)


async def rate_driver_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Save the passenger's driver rating once.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if is_duplicate_action(
        user_id,
        "rate_driver",
    ):
        await update.message.reply_text(
            "⏳ Your rating is already being processed."
        )
        return

    ride = get_latest_completed_ride(
        user_id
    )

    if ride is None:
        await update.message.reply_text(
            "❌ No recently completed ride found."
        )
        return

    ride_id = ride[0]
    driver_id = ride[1]

    try:
        rating = int(
            update.message.text[-1]
        )
    except (
        TypeError,
        ValueError,
        IndexError,
    ):
        await update.message.reply_text(
            "❌ Invalid rating."
        )
        return

    if rating not in {
        1,
        2,
        3,
        4,
        5,
    }:
        await update.message.reply_text(
            "❌ Please choose a rating "
            "between 1 and 5."
        )
        return

    rate_driver(
        ride_id,
        rating,
    )

    update_driver_rating(
        driver_id
    )

    await update.message.reply_text(
        f"⭐ Thank you! You rated your driver "
        f"{rating}/5.\n\n"
        "🙏 Thank you for helping improve "
        "HABESHAGO!",
        reply_markup=get_main_menu(),
    )