from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import (
    ADMIN_ID,
)

from app.services.system_health_service import (
    get_system_health,
)


async def show_live_statistics(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display HABESHAGO live operational statistics.

    Only the configured administrator may
    access this dashboard.
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
            "to view live statistics."
        )
        return

    report = get_system_health()
    metrics = report["metrics"]

    checked_at = report[
        "checked_at"
    ].strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    await update.message.reply_text(
        "📊 HABESHAGO LIVE STATISTICS\n\n"

        f"🕒 Updated: {checked_at}\n\n"

        "👥 USER NETWORK\n"
        f"🙋 Passengers: "
        f"{metrics['total_passengers']}\n"
        f"🚖 Registered Drivers: "
        f"{metrics['total_drivers']}\n"
        f"🟢 Online Drivers: "
        f"{metrics['online_drivers']}\n"
        f"✅ Available Drivers: "
        f"{metrics['available_drivers']}\n\n"

        "🚕 RIDE OPERATIONS\n"
        f"🚕 Active Rides: "
        f"{metrics['active_rides']}\n"
        f"🏁 Completed Rides Today: "
        f"{metrics['completed_rides_today']}\n\n"

        "━━━━━━━━━━━━━━\n"
        "📈 Live operational snapshot."
    )