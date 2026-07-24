import logging

from app.constants.ride_status import (
    ACCEPTED,
    DRIVER_ARRIVED,
    DRIVER_ARRIVING,
    TRIP_STARTED,
)

from app.database.database import (
    create_connection,
)

from app.state.active_ride_state import (
    active_rides,
)


logger = logging.getLogger(__name__)


ACTIVE_STATUSES = (
    ACCEPTED,
    DRIVER_ARRIVING,
    DRIVER_ARRIVED,
    TRIP_STARTED,
)


def get_active_rides_from_database():
    """
    Return all unfinished rides stored in SQLite.

    Each result contains enough information to
    rebuild HABESHAGO's in-memory active_rides state.
    """

    connection = create_connection()
    cursor = connection.cursor()

    placeholders = ", ".join(
        "?"
        for _ in ACTIVE_STATUSES
    )

    cursor.execute(
        f"""
        SELECT
            id,
            passenger_id,
            driver_id,
            pickup_latitude,
            pickup_longitude,
            destination_latitude,
            destination_longitude,
            distance,
            fare,
            service_type,
            status
        FROM rides
        WHERE status IN ({placeholders})
        ORDER BY id
        """,
        ACTIVE_STATUSES,
    )

    rides = cursor.fetchall()

    connection.close()

    return rides


def recover_active_rides():
    """
    Rebuild the in-memory active_rides dictionary
    from unfinished database rides.

    Returns the number of recovered rides.
    """

    database_rides = (
        get_active_rides_from_database()
    )

    # Clear any stale in-memory values before
    # rebuilding the state from SQLite.
    active_rides.clear()

    for ride in database_rides:
        (
            ride_id,
            passenger_id,
            driver_id,
            pickup_latitude,
            pickup_longitude,
            destination_latitude,
            destination_longitude,
            distance,
            fare,
            service_type,
            status,
        ) = ride

        active_rides[driver_id] = {
            "ride_id": ride_id,
            "passenger_id": passenger_id,
            "pickup": (
                pickup_latitude,
                pickup_longitude,
            ),
            "destination": (
                destination_latitude,
                destination_longitude,
            ),
            "distance": float(
                distance or 0
            ),
            "fare": float(
                fare or 0
            ),
            "service_type": (
                service_type or "fuel"
            ),
            "status": status,
            "recovered": True,
        }

        logger.info(
            (
                "Recovered active ride %s "
                "for driver %s and passenger %s "
                "with status %s."
            ),
            ride_id,
            driver_id,
            passenger_id,
            status,
        )

    return len(database_rides)