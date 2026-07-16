from telegram import Update
from telegram.ext import ContextTypes

from app.database.driver_repository import (
    set_driver_available,
    set_driver_unavailable,
    set_driver_online,
    set_driver_offline,
)

from app.keyboards.availability import (
    get_availability_keyboard,
)

from app.keyboards.availability import (
    get_availability_keyboard,
)

from app.keyboards.driver_menu import (
    get_driver_menu,
)

async def go_online(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Set the driver as available.
    """

    user_id = update.effective_user.id

    set_driver_online(user_id)
    set_driver_available(user_id)

    await update.message.reply_text(
        "🟢 You are now ONLINE.\n\n"
        "Passengers can now request rides from you.",
        reply_markup=get_driver_menu(),
    )

async def go_offline(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Set the driver as unavailable.
    """

    user_id = update.effective_user.id

    set_driver_offline(user_id)
    set_driver_unavailable(user_id)

    await update.message.reply_text(
        "🔴 You are now OFFLINE.\n\n"
        "You will no longer receive new ride requests.",
        reply_markup=get_driver_menu(),
    )

async def show_availability_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🚖 Driver Availability\n\n"
        "Choose your current status.",
        reply_markup=get_availability_keyboard(),
    )