from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.driver_dashboard import (
    get_driver_dashboard_keyboard,
)

from app.services.driver_dashboard_service import (
    get_driver_dashboard,
)

from app.state.user_context import (
    get_user_context,
)

RIDE_STATUS_LABELS = {
    "ACCEPTED": "✅ Driver Accepted",
    "DRIVER_ARRIVING": "🚗 Driving to Pickup",
    "DRIVER_ARRIVED": "📍 Waiting at Pickup",
    "TRIP_STARTED": "🚕 Trip in Progress",
}


async def show_driver_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the driver's context-aware
    business workspace.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    dashboard = get_driver_dashboard(driver_id)

    if dashboard is None:
        await update.message.reply_text(
            "❌ Driver profile not found.\n\n" "Please register as a driver first."
        )
        return

    user_context = get_user_context(driver_id)

    profile = dashboard["profile"]
    today = dashboard["today"]
    week = dashboard["week"]
    month = dashboard["month"]
    lifetime = dashboard["lifetime"]
    statistics = dashboard["statistics"]

    availability_status = (
        "🟢 Available" if profile["is_available"] else "🔴 Unavailable"
    )

    # ==========================================
    # CURRENT RIDE CONTEXT
    # ==========================================

    active_ride = user_context["active_driver_ride"]

    if active_ride is None:
        current_ride_section = (
            "🚕 CURRENT RIDE\n\n"
            "Status\n"
            "✅ Waiting for Ride\n\n"
            "Next Action\n"
            "🟢 Stay online to receive ride requests.\n\n"
        )
    else:
        ride_id = active_ride.get(
            "ride_id",
            "Unknown",
        )

        ride_status = active_ride.get(
            "status",
            "ACCEPTED",
        )

        status_display = RIDE_STATUS_LABELS.get(
            ride_status,
            ride_status,
        )

        next_action = {
            "ACCEPTED": "📍 Drive to the pickup location.",
            "DRIVER_ARRIVED": "👤 Wait for the passenger to board.",
            "TRIP_STARTED": "🏁 Drive safely and complete the ride.",
        }.get(
            ride_status,
            "🚖 Continue your current ride.",
        )

        current_ride_section = (
            "🚕 CURRENT RIDE\n\n"
            "Status\n"
            f"{status_display}\n\n"
            "Ride\n"
            f"#{ride_id}\n\n"
            "Next Action\n"
            f"{next_action}\n\n"
        )

    # ==========================================
    # DRIVER WORKSPACE
    # ==========================================

    await update.message.reply_text(
        "🚖 HABESHAGO DRIVER WORKSPACE\n\n"
        "📍 CURRENT STATUS\n"
        f"{availability_status}\n\n"
        f"{current_ride_section}"
        "━━━━━━━━━━━━━━\n\n"
        "👤 DRIVER PROFILE\n"
        f"👤 Name: {profile['full_name']}\n"
        f"📱 Phone: "
        f"{profile['phone_number'] or 'Not provided'}\n"
        f"🚗 Vehicle: {profile['vehicle']}\n"
        f"📅 Year: {profile['vehicle_year']}\n"
        f"🎨 Color: {profile['vehicle_color']}\n"
        f"🔢 Plate: {profile['plate_number']}\n"
        f"⭐ Rating: {profile['rating']:.2f}\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "💰 EARNINGS OVERVIEW\n\n"
        "📅 Today\n"
        f"🚖 Rides: {today['completed_rides']}\n"
        f"💰 Earnings: "
        f"{today['net_earnings']:,.2f} ETB\n\n"
        "📊 Last 7 Days\n"
        f"🚖 Rides: {week['completed_rides']}\n"
        f"💰 Earnings: "
        f"{week['net_earnings']:,.2f} ETB\n\n"
        "📈 Current Month\n"
        f"🚖 Rides: {month['completed_rides']}\n"
        f"💰 Earnings: "
        f"{month['net_earnings']:,.2f} ETB\n\n"
        "🏆 Lifetime\n"
        f"🚖 Completed Rides: "
        f"{lifetime['completed_rides']}\n"
        f"💵 Gross Fares: "
        f"{lifetime['gross_fares']:,.2f} ETB\n"
        f"📉 Commission Paid: "
        f"{lifetime['commission_paid']:,.2f} ETB\n"
        f"💰 Net Earnings: "
        f"{lifetime['net_earnings']:,.2f} ETB\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "📊 PERFORMANCE STATISTICS\n\n"
        f"💵 Average Fare: "
        f"{statistics['average_fare']:,.2f} ETB\n"
        f"🛣 Average Trip Distance: "
        f"{statistics['average_distance']:.2f} km\n"
        f"🏆 Highest Fare: "
        f"{statistics['highest_fare']:,.2f} ETB\n"
        f"🚖 Longest Trip: "
        f"{statistics['longest_trip']:.2f} km\n\n"
        "━━━━━━━━━━━━━━\n"
        "🚖 Your driver workspace is ready.",
        reply_markup=get_driver_dashboard_keyboard(),
    )
