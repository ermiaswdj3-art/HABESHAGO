from datetime import datetime

from app.database.database import (
    DATABASE_ERROR_TYPES,
    create_connection,
)

from app.services.admin_operations_service import (
    get_admin_operations_snapshot,
)

HABESHAGO_VERSION = "v0.50"


def check_database_health():
    """
    Verify that HABESHAGO can connect to SQLite
    and execute a simple query.
    """

    connection = None

    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1")

        result = cursor.fetchone()

        return result == (1,)

    except DATABASE_ERROR_TYPES:
        return False

    finally:
        if connection is not None:
            connection.close()


def get_system_metrics():
    """
    Return compatibility metrics derived from the
    canonical Admin Operations Platform.

    This function remains available for existing
    system-health handlers, but it no longer owns
    separate business-count SQL.
    """

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

    return {
        "total_passengers": passengers["total"],
        "total_drivers": registration["total"],
        "online_drivers": operations["online"],
        "available_drivers": (
            operations["available"]
        ),
        "active_rides": rides["active"],
        "completed_rides_today": (
            rides["completed_today"]
        ),
        "pending_ride_offers": (
            offers["pending"]
        ),
        "unsettled_completed_rides": (
            settlements["not_settled"]
        ),
    }


def get_stale_active_rides(
    stale_minutes=30,
):
    """
    Return active rides that have not progressed
    within the configured time window.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            passenger_id,
            driver_id,
            status,
            accepted_at,
            arrived_at,
            started_at
        FROM rides
        WHERE status IN (
            'ACCEPTED',
            'DRIVER_ARRIVING',
            'DRIVER_ARRIVED',
            'TRIP_STARTED'
        )
          AND COALESCE(
              started_at,
              arrived_at,
              accepted_at,
              created_at
          ) < DATETIME(
              'now',
              'localtime',
              ?
          )
        ORDER BY id DESC
        """,
        (
            f"-{int(stale_minutes)} minutes",
        ),
    )

    stale_rides = cursor.fetchall()

    connection.close()

    return stale_rides


def get_system_health():
    """
    Build the complete HABESHAGO system-health
    report used by the administrator dashboard.
    """

    database_connected = check_database_health()

    try:
        metrics = get_system_metrics()
        metrics_available = True
    except DATABASE_ERROR_TYPES:
        metrics = {
            "total_passengers": 0,
            "total_drivers": 0,
            "online_drivers": 0,
            "available_drivers": 0,
            "active_rides": 0,
            "completed_rides_today": 0,
            "pending_ride_offers": 0,
            "unsettled_completed_rides": 0,
        }
        metrics_available = False

    try:
        stale_rides = get_stale_active_rides()
        stale_check_available = True
    except DATABASE_ERROR_TYPES:
        stale_rides = []
        stale_check_available = False

    return {
        "version": HABESHAGO_VERSION,
        "checked_at": datetime.now(),


        # TODO:
        # Replace this runtime assumption with a real
        # heartbeat or process-health signal in production.
        "bot_online": True,

        
        "database_connected": database_connected,
        "metrics_available": metrics_available,
        "driver_dispatch_ready": (
            database_connected
        ),
        "ride_queue_healthy": (
            database_connected
            and stale_check_available
            and len(stale_rides) == 0
        ),
        "stale_check_available": stale_check_available,
        "stale_active_rides": stale_rides,
        "stale_active_ride_count": len(
            stale_rides
        ),
        "metrics": metrics,
    }