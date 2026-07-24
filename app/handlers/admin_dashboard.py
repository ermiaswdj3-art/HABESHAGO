from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import (
    ADMIN_ID,
)

from app.keyboards.admin_dashboard import (
    get_admin_dashboard_keyboard,
)


async def show_admin_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the HABESHAGO administrator
    operations dashboard.

    Only the configured administrator may
    open this dashboard.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if (
        ADMIN_ID is None
        or str(user_id) != str(ADMIN_ID)
    ):
        await update.message.reply_text(
            "❌ You are not authorized "
            "to open the administrator dashboard."
        )
        return

    await update.message.reply_text(
        "🛠 HABESHAGO OPERATIONS CENTER\n\n"
        "Welcome, Administrator.\n\n"
        "Choose an operation below.",
        reply_markup=get_admin_dashboard_keyboard(),
    )