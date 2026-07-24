from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import (
    ADMIN_ID,
)

from app.database.database import (
    create_connection,
)


ACTIVE_RIDE_STATUSES = (
    "ACCEPTED",
    "DRIVER_ARRIVING",
    "DRIVER_ARRIVED",
    "TRIP_STARTED",
)


STATUS_LABELS = {
    "ACCEPTED": "✅ Driver Accepted",
    "DRIVER_ARRIVING": "🚗 Driver Arriving",
    "DRIVER_ARRIVED": "📍 Driver Arrived",
    "TRIP_STARTED": "🚕 Trip Started",
}


def get_active_rides():
    """
    Return active rides with passenger and
    driver names for the Operations Center.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            rides.id,
            rides.passenger_id,
            passengers.full_name,
            rides.driver_id,
            drivers.full_name,
            rides.status,
            rides.distance,
            rides.fare,
            rides.accepted_at,
            rides.arrived_at,
            rides.started_at
        FROM rides

        LEFT JOIN passengers
            ON passengers.telegram_id
            = rides.passenger_id

        LEFT JOIN drivers
            ON drivers.telegram_id
            = rides.driver_id

        WHERE rides.status IN (
            'ACCEPTED',
            'DRIVER_ARRIVING',
            'DRIVER_ARRIVED',
            'TRIP_STARTED'
        )

        ORDER BY
            COALESCE(
                rides.accepted_at,
                rides.created_at
            ) ASC
        """
    )

    rides = cursor.fetchall()

    connection.close()

    return rides


def get_latest_progress_time(
    status,
    accepted_at,
    arrived_at,
    started_at,
):
    """
    Return the timestamp representing the
    ride's latest lifecycle progress.
    """

    if (
        status == "TRIP_STARTED"
        and started_at
    ):
        return started_at

    if (
        status == "DRIVER_ARRIVED"
        and arrived_at
    ):
        return arrived_at

    return accepted_at or "Not recorded"


async def show_active_ride_queue(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display all active rides in a
    human-friendly dispatcher view.
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

    rides = get_active_rides()

    if not rides:
        await update.message.reply_text(
            "📋 ACTIVE RIDE QUEUE\n\n"
            "✅ There are currently no active rides."
        )
        return

    message_parts = [
        "📋 HABESHAGO ACTIVE RIDE QUEUE",
        "",
        f"🚕 Active Rides: {len(rides)}",
        "━━━━━━━━━━━━━━",
    ]

    for ride in rides:
        (
            ride_id,
            passenger_id,
            passenger_name,
            driver_id,
            driver_name,
            status,
            distance,
            fare,
            accepted_at,
            arrived_at,
            started_at,
        ) = ride

        passenger_display = (
            passenger_name
            or f"Passenger #{passenger_id}"
        )

        driver_display = (
            driver_name
            or f"Driver #{driver_id}"
        )

        status_display = STATUS_LABELS.get(
            status,
            status,
        )

        latest_progress = (
            get_latest_progress_time(
                status,
                accepted_at,
                arrived_at,
                started_at,
            )
        )

        message_parts.extend(
            [
                "",
                f"🚖 Ride #{ride_id}",
                "",
                "👤 Passenger",
                passenger_display,
                "",
                "🚗 Driver",
                driver_display,
                "",
                f"📌 Status: {status_display}",
                f"🕒 Latest Progress: {latest_progress}",
                "",
                f"🛣 Trip Distance: {distance:.2f} km",
                f"💰 Estimated Fare: {fare:,.2f} ETB",
                "",
                "━━━━━━━━━━━━━━",
            ]
        )

    message = "\n".join(
        message_parts
    )

    await update.message.reply_text(
        message
    )