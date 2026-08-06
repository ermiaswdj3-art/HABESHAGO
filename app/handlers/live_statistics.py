"""
HABESHAGO Telegram Live Statistics Handler

Displays the canonical platform-wide business operations
snapshot from the shared Admin Operations Platform.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import (
    ADMIN_ID,
)

from app.services.admin_operations_service import (
    get_admin_operations_snapshot,
)


async def show_live_statistics(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the canonical HABESHAGO operations snapshot.

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

    passengers = snapshot["passengers"]

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

    await update.message.reply_text(
        "📊 HABESHAGO LIVE OPERATIONS\n\n"

        f"🕒 Generated: {generated_at}\n"
        "🗄 Source: Shared Platform Database\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "👥 PASSENGERS\n"
        f"Total: {passengers['total']}\n\n"

        "🚖 DRIVERS\n"
        f"Total: {registration['total']}\n"
        f"Approved: {registration['approved']}\n"
        "Verification Pending: "
        f"{registration['verification_pending']}\n"
        f"Rejected: {registration['rejected']}\n"
        f"Suspended: {registration['suspended']}\n\n"

        "DRIVER OPERATIONS\n"
        f"Online: {operations['online']}\n"
        f"Available: {operations['available']}\n"
        f"Unavailable: {operations['unavailable']}\n"
        f"Offline: {operations['offline']}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "🚕 RIDES\n"
        f"Total: {rides['total']}\n"
        f"Requested: {rides['requested']}\n"
        f"Active: {rides['active']}\n"
        f"Completed: {rides['completed']}\n"
        f"Cancelled: {rides['cancelled']}\n"
        f"Expired: {rides['expired']}\n\n"

        "TODAY\n"
        f"Completed: {rides['completed_today']}\n"
        f"Cancelled: {rides['cancelled_today']}\n"
        f"Expired: {rides['expired_today']}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "📨 RIDE OFFERS\n"
        f"Total: {offers['total']}\n"
        f"Pending: {offers['pending']}\n"
        f"Accepted: {offers['accepted']}\n"
        f"Rejected: {offers['rejected']}\n"
        f"Expired: {offers['expired']}\n"
        f"Cancelled: {offers['cancelled']}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "💰 SETTLEMENTS\n"
        f"Completed Rides: "
        f"{settlements['completed_rides']}\n"
        f"Settled: {settlements['settled']}\n"
        f"Not Settled: {settlements['not_settled']}\n"
        f"Gross Fares: "
        f"{settlements['gross_fares']:,.2f} ETB\n"
        f"Commission: "
        f"{settlements['commission']:,.2f} ETB\n"
        f"Driver Earnings: "
        f"{settlements['driver_earnings']:,.2f} ETB\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "PLATFORM READINESS\n"
        f"Dispatch: {dispatch_status}\n"
        f"Settlements: {settlement_status}\n"
        f"Operational Alerts: "
        f"{snapshot['alert_count']}"
    )