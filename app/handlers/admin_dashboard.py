"""
HABESHAGO Telegram Admin Dashboard Handler

Displays the shared platform-wide Admin Operations
workspace for the configured HABESHAGO administrator.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import (
    ADMIN_ID,
)

from app.keyboards.admin_dashboard import (
    get_admin_dashboard_keyboard,
)

from app.services.admin_operations_service import (
    get_admin_operations_snapshot,
)


async def show_admin_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the HABESHAGO administrator workspace.

    Only the configured administrator may access it.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if (
        ADMIN_ID is None
        or str(user_id) != str(ADMIN_ID)
    ):
        await update.message.reply_text(
            "❌ Administrator access required."
        )
        return

    snapshot = (
        get_admin_operations_snapshot()
    )

    registration = snapshot[
        "drivers"
    ]["registration"]

    operations = snapshot[
        "drivers"
    ]["operations"]

    rides = snapshot["rides"]

    offers = snapshot["ride_offers"]

    settlements = snapshot["settlements"]

    readiness = snapshot["readiness"]

    generated_at = snapshot[
        "generated_at"
    ].strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    dispatch_status = (
        "✅ Ready"
        if readiness["dispatch_ready"]
        else "❌ Not Ready"
    )

    settlement_status = (
        "✅ Healthy"
        if readiness["settlements_healthy"]
        else "⚠️ Review Required"
    )

    if snapshot["alerts"]:
        alert_lines = [
            (
                f"• {alert['code']}: "
                f"{alert['message']}"
            )
            for alert in snapshot["alerts"]
        ]

        alert_section = (
            "\n\n🚨 OPERATIONAL ALERTS\n"
            + "\n".join(alert_lines)
        )

    else:
        alert_section = (
            "\n\n✅ No operational alerts."
        )

    await update.message.reply_text(
        "🛡 HABESHAGO OPERATIONS CENTER\n\n"

        f"🕒 Snapshot: {generated_at}\n"
        "🗄 Source: Shared Platform Database\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "PLATFORM OVERVIEW\n"
        f"👥 Passengers: "
        f"{snapshot['passengers']['total']}\n"
        f"🚖 Drivers: {registration['total']}\n"
        f"✅ Approved Drivers: "
        f"{registration['approved']}\n"
        f"🟢 Available Drivers: "
        f"{operations['available']}\n\n"

        "RIDE OPERATIONS\n"
        f"🚕 Active Rides: {rides['active']}\n"
        f"📨 Pending Offers: {offers['pending']}\n"
        f"🏁 Completed Rides: {rides['completed']}\n"
        f"❌ Cancelled Rides: {rides['cancelled']}\n\n"

        "FINANCIAL OPERATIONS\n"
        f"✅ Settled Rides: "
        f"{settlements['settled']}\n"
        f"⚠️ Unsettled Completed Rides: "
        f"{settlements['not_settled']}\n"
        f"💰 Platform Commission: "
        f"{settlements['commission']:,.2f} ETB\n\n"

        "PLATFORM READINESS\n"
        f"Dispatch: {dispatch_status}\n"
        f"Settlements: {settlement_status}"
        f"{alert_section}",
        reply_markup=(
            get_admin_dashboard_keyboard(
                user_id
            )
        ),
    )