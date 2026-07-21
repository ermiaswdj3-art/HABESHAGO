from telegram import Update
from telegram.ext import ContextTypes

from app.services.driver_dashboard_service import (
    get_driver_dashboard,
)


async def show_driver_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the driver's complete business dashboard.
    """

    if update.message is None:
        return

    driver_id = update.effective_user.id

    dashboard = get_driver_dashboard(
        driver_id
    )

    if dashboard is None:
        await update.message.reply_text(
            "❌ Driver profile not found.\n\n"
            "Please register as a driver first."
        )
        return

    profile = dashboard["profile"]
    today = dashboard["today"]
    week = dashboard["week"]
    month = dashboard["month"]
    lifetime = dashboard["lifetime"]
    statistics = dashboard["statistics"]

    availability_status = (
        "🟢 Available"
        if profile["is_available"]
        else "🔴 Unavailable"
    )

    await update.message.reply_text(
        "🚖 HABESHAGO DRIVER DASHBOARD\n\n"

        "👤 DRIVER PROFILE\n"
        f"👤 Name: {profile['full_name']}\n"
        f"📱 Phone: {profile['phone_number'] or 'Not provided'}\n"
        f"🚗 Vehicle: {profile['vehicle']}\n"
        f"📅 Year: {profile['vehicle_year']}\n"
        f"🎨 Color: {profile['vehicle_color']}\n"
        f"🔢 Plate: {profile['plate_number']}\n"
        f"⭐ Rating: {profile['rating']:.2f}\n"
        f"🟢 Status: {availability_status}\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "💰 EARNINGS OVERVIEW\n\n"

        "📅 Today\n"
        f"🚖 Rides: {today['completed_rides']}\n"
        f"💰 Earnings: {today['net_earnings']:,.2f} ETB\n\n"

        "📊 Last 7 Days\n"
        f"🚖 Rides: {week['completed_rides']}\n"
        f"💰 Earnings: {week['net_earnings']:,.2f} ETB\n\n"

        "📈 Current Month\n"
        f"🚖 Rides: {month['completed_rides']}\n"
        f"💰 Earnings: {month['net_earnings']:,.2f} ETB\n\n"

        "🏆 Lifetime\n"
        f"🚖 Completed Rides: {lifetime['completed_rides']}\n"
        f"💵 Gross Fares: {lifetime['gross_fares']:,.2f} ETB\n"
        f"📉 Commission Paid: {lifetime['commission_paid']:,.2f} ETB\n"
        f"💰 Net Earnings: {lifetime['net_earnings']:,.2f} ETB\n\n"

        "━━━━━━━━━━━━━━\n\n"

        "📊 PERFORMANCE STATISTICS\n\n"
        f"💵 Average Fare: {statistics['average_fare']:,.2f} ETB\n"
        f"🛣 Average Trip Distance: {statistics['average_distance']:.2f} km\n"
        f"🏆 Highest Fare: {statistics['highest_fare']:,.2f} ETB\n"
        f"🚖 Longest Trip: {statistics['longest_trip']:.2f} km\n\n"

        "━━━━━━━━━━━━━━\n"
        "📍 Ready to receive new rides."
    )