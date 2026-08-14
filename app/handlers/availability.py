"""
HABESHAGO Driver Availability Handlers

Telegram handlers for the canonical Driver Availability
and Lifecycle Platform.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.availability import (
    get_availability_keyboard,
)

from app.keyboards.driver_dashboard import (
    get_driver_dashboard_keyboard,
)

from app.services.driver_availability_service import (
    make_driver_available,
    make_driver_offline,
)


async def go_online(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Put an eligible driver online and available.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    try:
        state = make_driver_available(
            driver_id
        )

    except ValueError as error:
        await update.message.reply_text(
            "❌ Unable to go online.\n\n"
            f"{error}",
            reply_markup=get_driver_dashboard_keyboard(),
        )
        return

    await update.message.reply_text(
        "🟢 You are now ONLINE and AVAILABLE.\n\n"
        "You can receive new HABESHAGO ride offers.",
        reply_markup=get_driver_dashboard_keyboard(),
    )


async def go_offline(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Put a driver fully offline.

    Drivers with active rides cannot go offline.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    try:
        state = make_driver_offline(
            driver_id
        )

    except ValueError as error:
        await update.message.reply_text(
            "❌ Unable to go offline.\n\n"
            f"{error}",
            reply_markup=get_driver_dashboard_keyboard(),
        )
        return

    await update.message.reply_text(
        "🔴 You are now OFFLINE.\n\n"
        "You will not receive new HABESHAGO ride offers.",
        reply_markup=get_driver_dashboard_keyboard(),
    )


async def show_availability_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the driver availability controls.
    """

    if update.message is None:
        return

    await update.message.reply_text(
        "🚖 Driver Availability\n\n"
        "Choose your current operational status.",
        reply_markup=get_availability_keyboard(),
    )