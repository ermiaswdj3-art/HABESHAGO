from telegram import Update
from telegram.ext import ContextTypes

from app.database.ride_repository import (
    get_latest_completed_ride,
    rate_driver,
)

from app.database.driver_repository import (
    update_driver_rating,
)

from app.keyboards.main_menu import get_main_menu


async def rate_driver_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    ride = get_latest_completed_ride(user_id)

    if ride is None:
        await update.message.reply_text(
            "❌ No recently completed ride found."
        )
        return

    ride_id = ride[0]
    driver_id = ride[1]

    rating = int(update.message.text[-1])

    rate_driver(
        ride_id,
        rating,
    )

    update_driver_rating(driver_id)

    await update.message.reply_text(
        f"⭐ Thank you! You rated your driver {rating}/5.\n\n"
        "🙏 Thank you for helping improve HABESHAGO!",
        reply_markup=get_main_menu(),
    )