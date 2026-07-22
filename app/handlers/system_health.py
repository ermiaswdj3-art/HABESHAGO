from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import ADMIN_ID

from app.services.system_health_service import (
    get_system_health,
)


async def system_health(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the HABESHAGO System Health
    dashboard.

    Only the administrator may use this
    command.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    # Deny access when ADMIN_ID is missing
    # or when the current user is not the admin.
    if (
        ADMIN_ID is None
        or str(user_id) != str(ADMIN_ID)
    ):
        await update.message.reply_text(
            "❌ You are not authorized "
            "to use this command."
        )
        return

    report = get_system_health()

    bot_status = (
        "🟢 Online"
        if report["bot_online"]
        else "🔴 Offline"
    )

    if all(
       (
           report["bot_online"],
           report["database_connected"],
           report["metrics_available"],
           report["driver_dispatch_ready"],
           report["ride_queue_healthy"],
        )
    ):
        overall_status = "🟢 HEALTHY"
    elif (
        report["database_connected"]
        and report["bot_online"]
    ):
        overall_status = "🟡 WARNING"
    else:
        overall_status = "🔴 DEGRADED"

    checked_at = report[
        "checked_at"
    ].strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    database = (
        "🟢 Connected"
        if report["database_connected"]
        else "🔴 Offline"
    )

    metrics = (
        "🟢 Available"
        if report["metrics_available"]
        else "🔴 Unavailable"
    )

    dispatch = (
        "🟢 Ready"
        if report["driver_dispatch_ready"]
        else "🔴 Offline"
    )

    stale_count = report[
        "stale_active_ride_count"
    ]

    if not report["stale_check_available"]:
        queue = "🔴 Check unavailable"

    elif stale_count == 1:
        queue = "🟡 1 stale active ride"

    elif stale_count > 1:
        queue = (
            f"🟡 {stale_count} stale active rides"
        )

    else:
        queue = "🟢 No stalled rides"

    metrics_data = report["metrics"]

    stale_details = ""

    if stale_count > 0:
        stale_lines = []

        for ride in report[
            "stale_active_rides"
        ][:5]:
            (
                ride_id,
                passenger_id,
                driver_id,
                status,
                accepted_at,
                arrived_at,
                started_at,
            ) = ride

            stale_lines.append(
                f"• Ride #{ride_id} — {status}"
            )

        stale_details = (
            "\n\n⚠️ STALE RIDES\n"
            + "\n".join(stale_lines)
        )

    system_is_healthy = all(
        (
            report["database_connected"],
            report["metrics_available"],
            report["driver_dispatch_ready"],
            report["ride_queue_healthy"],
        )
    )

    if system_is_healthy:
        footer = (
            "\n\n━━━━━━━━━━━━━━\n"
            "✅ HABESHAGO is operating normally."
        )
    else:
        footer = (
            "\n\n━━━━━━━━━━━━━━\n"
            "⚠️ Attention required.\n"
            "Please review the system status."
        )

    await update.message.reply_text(
        "🩺 HABESHAGO System Health\n\n"

        f"Overall Status: {overall_status}\n\n"

        f"🚖 Version: {report['version']}\n"
        f"🕒 Checked: {checked_at}\n\n"

        "SYSTEM STATUS\n"
        f"🤖 Bot: {bot_status}\n"
        f"🗄 Database: {database}\n"
        f"📊 Metrics: {metrics}\n"
        f"🚖 Driver Dispatch: {dispatch}\n"
        f"📦 Ride Queue: {queue}\n\n"

        "LIVE METRICS\n"
        f"👥 Passengers: "
        f"{metrics_data['total_passengers']}\n"
        f"🚖 Drivers: "
        f"{metrics_data['total_drivers']}\n"
        f"🟢 Online Drivers: "
        f"{metrics_data['online_drivers']}\n"
        f"✅ Available Drivers: "
        f"{metrics_data['available_drivers']}\n"
        f"🚕 Active Rides: "
        f"{metrics_data['active_rides']}\n"
        f"🏁 Completed Rides Today: "
        f"{metrics_data['completed_rides_today']}"
        f"{stale_details}"
        f"{footer}"
    )