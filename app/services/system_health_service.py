import sqlite3
from datetime import datetime

from app.database.database import (
    create_connection,
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

    except sqlite3.Error:
        return False

    finally:
        if connection is not None:
            connection.close()


def get_system_metrics():
    """
    Return basic operational metrics used by
    the administrator health dashboard.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM passengers
        """
    )
    total_passengers = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM drivers
        """
    )
    total_drivers = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM drivers
        WHERE is_online = 1
        """
    )
    online_drivers = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM drivers
        WHERE is_available = 1
        """
    )
    available_drivers = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM rides
        WHERE status IN (
            'ACCEPTED',
            'DRIVER_ARRIVING',
            'DRIVER_ARRIVED',
            'TRIP_STARTED'
        )
        """
    )
    active_rides = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM rides
        WHERE status = 'TRIP_COMPLETED'
          AND DATE(completed_at)
              = DATE('now', 'localtime')
        """
    )
    completed_rides_today = cursor.fetchone()[0]

    connection.close()

    return {
        "total_passengers": int(
            total_passengers or 0
        ),
        "total_drivers": int(
            total_drivers or 0
        ),
        "online_drivers": int(
            online_drivers or 0
        ),
        "available_drivers": int(
            available_drivers or 0
        ),
        "active_rides": int(
            active_rides or 0
        ),
        "completed_rides_today": int(
            completed_rides_today or 0
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
    except sqlite3.Error:
        metrics = {
            "total_passengers": 0,
            "total_drivers": 0,
            "online_drivers": 0,
            "available_drivers": 0,
            "active_rides": 0,
            "completed_rides_today": 0,
        }
        metrics_available = False

    try:
        stale_rides = get_stale_active_rides()
        stale_check_available = True
    except sqlite3.Error:
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