"""
HABESHAGO Active Ride Queue Handler

Displays canonical active HABESHAGO Rides for the
configured Operations administrator.

Ride identity, lifecycle, fare, route, driver context,
and live GPS come from the shared Admin Operations
Platform. This handler does not maintain competing
Ride queries or lifecycle state.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import (
    ADMIN_ID,
)

from app.services.admin_operations_service import (
    get_admin_operations_snapshot,
)


STATUS_LABELS = {
    "ACCEPTED": "Driver Accepted",
    "DRIVER_ARRIVING": "Driver Arriving",
    "DRIVER_ARRIVED": "Driver Arrived",
    "TRIP_STARTED": "Trip Started",
}


def _format_coordinate(
    value,
) -> str:
    """
    Return one coordinate for Operations display.
    """

    if value is None:
        return "Not available"

    try:
        return f"{float(value):.6f}"

    except (TypeError, ValueError):
        return str(value)


def _format_timestamp(
    value,
) -> str:
    """
    Return one lifecycle timestamp for display.
    """

    if value in (
        None,
        "",
    ):
        return "Not recorded"

    return str(value)


def _format_active_ride(
    ride: dict,
) -> str:
    """
    Build one human-readable canonical Ride block.
    """

    ride_id = ride.get(
        "ride_id"
    )

    passenger_id = ride.get(
        "passenger_id"
    )

    driver_id = ride.get(
        "driver_id"
    )

    status = ride.get(
        "status"
    )

    status_display = (
        STATUS_LABELS.get(
            status,
            status or "Unknown",
        )
    )

    driver = (
        ride.get("driver")
        or {}
    )

    driver_name = (
        driver.get("full_name")
        or f"Driver #{driver_id}"
    )

    service_type = (
        ride.get("service_type")
        or "Not recorded"
    )

    distance = ride.get(
        "distance"
    )

    fare = ride.get(
        "fare"
    )

    pickup = (
        ride.get("pickup")
        or {}
    )

    destination = (
        ride.get("destination")
        or {}
    )

    live_location = ride.get(
        "live_location"
    )

    try:
        distance_display = (
            f"{float(distance or 0):.2f} km"
        )
    except (TypeError, ValueError):
        distance_display = str(
            distance
        )

    try:
        fare_display = (
            f"{float(fare or 0):,.2f} ETB"
        )
    except (TypeError, ValueError):
        fare_display = str(
            fare
        )

    lines = [
        f"🚕 Ride #{ride_id}",
        "",
        f"👤 Passenger: #{passenger_id}",
        (
            "🚗 Driver: "
            f"{driver_name} (#{driver_id})"
        ),
        f"📌 Status: {status_display}",
        f"🚘 Service: {service_type}",
        "",
        (
            "📍 Pickup: "
            f"{_format_coordinate(pickup.get('latitude'))}, "
            f"{_format_coordinate(pickup.get('longitude'))}"
        ),
        (
            "🏁 Destination: "
            f"{_format_coordinate(destination.get('latitude'))}, "
            f"{_format_coordinate(destination.get('longitude'))}"
        ),
        "",
        f"🛣 Distance: {distance_display}",
        f"💰 Fare: {fare_display}",
        "",
        "🕒 Lifecycle",
        (
            "Accepted: "
            f"{_format_timestamp(ride.get('accepted_at'))}"
        ),
        (
            "Arrived: "
            f"{_format_timestamp(ride.get('arrived_at'))}"
        ),
        (
            "Started: "
            f"{_format_timestamp(ride.get('started_at'))}"
        ),
    ]

    if live_location is None:
        lines.extend(
            [
                "",
                "📡 Live GPS: Not currently available",
            ]
        )

    else:
        lines.extend(
            [
                "",
                (
                    "📡 Live GPS: "
                    f"{live_location.get('status') or 'live'}"
                ),
                (
                    "Location: "
                    f"{_format_coordinate(live_location.get('latitude'))}, "
                    f"{_format_coordinate(live_location.get('longitude'))}"
                ),
                (
                    "Recorded: "
                    f"{_format_timestamp(live_location.get('recorded_at'))}"
                ),
            ]
        )

    return "\n".join(
        lines
    )


async def show_active_ride_queue(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display canonical active Rides to the configured
    HABESHAGO Operations administrator.
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
            "to view the active ride queue."
        )
        return

    snapshot = (
        get_admin_operations_snapshot()
    )

    rides = snapshot.get(
        "active_rides",
        [],
    )

    aggregate_active_count = (
        snapshot.get(
            "rides",
            {},
        ).get(
            "active",
            0,
        )
    )

    if aggregate_active_count != len(
        rides
    ):
        await update.message.reply_text(
            "⚠️ Operations consistency check failed. "
            "Active Ride totals do not match the "
            "canonical Ride detail queue."
        )
        return

    if not rides:
        await update.message.reply_text(
            "📋 HABESHAGO ACTIVE RIDE QUEUE\n\n"
            "✅ There are currently no canonical "
            "active rides."
        )
        return

    await update.message.reply_text(
        "📋 HABESHAGO ACTIVE RIDE QUEUE\n\n"
        f"🚕 Active Rides: {len(rides)}\n"
        "Source: Canonical Operations Platform"
    )

    for ride in rides:
        await update.message.reply_text(
            _format_active_ride(
                ride
            )
        )
