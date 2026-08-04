"""
HABESHAGO Telegram Driver Dashboard Handler

Displays the database-backed driver workspace using the
canonical Driver Dashboard Service contract.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.constants.ride_states import (
    RideState,
)

from app.keyboards.driver_dashboard import (
    get_driver_dashboard_keyboard,
)

from app.services.driver_dashboard_service import (
    get_driver_dashboard,
)

from app.services.ride_guidance_service import (
    get_ride_guidance,
)

from app.services.vehicle_management_service import (
    get_driver_vehicle_management,
)

from app.state.user_context import (
    get_user_context,
)


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

    vehicle_management = get_driver_vehicle_management(driver_id)

    if dashboard is None:
        await update.message.reply_text(
            "❌ Driver profile not found.\n\n" "Please register as a driver first."
        )
        return

    user_context = get_user_context(driver_id)

    profile = dashboard["profile"]
    active_vehicle = vehicle_management["active_vehicle"]
    status = dashboard["status"]

    today = dashboard["today"]
    week = dashboard["week"]
    month = dashboard["month"]
    lifetime = dashboard["lifetime"]
    statistics = dashboard["statistics"]

    status_icons = {
        "offline": "🔴",
        "available": "🟢",
        "unavailable": "🟡",
    }

    status_icon = status_icons.get(
        status["code"],
        "⚪",
    )

    availability_status = f"{status_icon} {status['label']}"

    # ==========================================
    # CURRENT RIDE CONTEXT
    # ==========================================

    active_ride = user_context["active_driver_ride"]

    if active_ride is None:
        guidance = get_ride_guidance(None)

        current_ride_section = (
            "🚕 CURRENT RIDE\n\n"
            "Status\n"
            f"{guidance['status']}\n\n"
            "Mission\n"
            f"{guidance['mission']}\n\n"
            "Next Action\n"
            f"{guidance['next_action']}\n\n"
        )

    else:
        ride_id = active_ride.get(
            "ride_id",
            "Unknown",
        )

        ride_status = active_ride.get(
            "status",
            RideState.DRIVER_ACCEPTED,
        )

        guidance = get_ride_guidance(ride_status)

        current_ride_section = (
            "🚕 CURRENT RIDE\n\n"
            "Status\n"
            f"{guidance['status']}\n\n"
            "Ride\n"
            f"#{ride_id}\n\n"
            "Mission\n"
            f"{guidance['mission']}\n\n"
            "Next Action\n"
            f"{guidance['next_action']}\n\n"
        )

    # ==========================================
    # DRIVER WORKSPACE
    # ==========================================

    if active_vehicle is None:
        vehicle_section = (
            "🚗 VEHICLE MANAGEMENT\n\n" "No active vehicle is currently registered.\n\n"
        )
    else:
        vehicle_type = active_vehicle["vehicle_type"].replace("_", " ").title()

    vehicle_status = active_vehicle["verification_status"].replace("_", " ").title()

    vehicle_section = (
        "🚗 VEHICLE MANAGEMENT\n\n"
        f"🚘 Vehicle: "
        f"{active_vehicle['display_name']}\n"
        f"📂 Type: {vehicle_type}\n"
        f"🏷 Category: "
        f"{active_vehicle['category'].title()}\n"
        f"📅 Year: "
        f"{active_vehicle['manufacturing_year']}\n"
        f"🎨 Color: "
        f"{active_vehicle['color']}\n"
        f"🔢 Plate: "
        f"{active_vehicle['plate']['number']}\n"
        f"🛡 Verification: {vehicle_status}\n"
        f"✅ Active: "
        f"{'Yes' if active_vehicle['is_active'] else 'No'}\n"
        f"🚖 Operational: "
        f"{'Yes' if active_vehicle['can_operate'] else 'No'}\n"
        f"📚 Registered Vehicles: "
        f"{vehicle_management['vehicle_count']}\n\n"
    )

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
        f"⭐ Rating: {profile['rating']:.2f}\n\n"
        "━━━━━━━━━━━━━━\n\n"
        f"{vehicle_section}"
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
