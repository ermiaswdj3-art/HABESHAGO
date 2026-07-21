from app.constants.ride_status import (
    TRIP_COMPLETED,
)

from app.database.database import (
    create_connection,
)


def get_driver_statistics(driver_id):
    """
    Return overall driver statistics.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(AVG(fare), 0),
            COALESCE(AVG(distance), 0),
            COALESCE(MAX(fare), 0),
            COALESCE(MAX(distance), 0)
        FROM rides
        WHERE driver_id = ?
          AND status = ?
        """,
        (
            driver_id,
            TRIP_COMPLETED,
        ),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {
            "completed_rides": 0,
            "average_fare": 0.0,
            "average_distance": 0.0,
            "highest_fare": 0.0,
            "longest_trip": 0.0,
        }

    return {
        "completed_rides": int(row[0] or 0),
        "average_fare": float(row[1] or 0),
        "average_distance": float(row[2] or 0),
        "highest_fare": float(row[3] or 0),
        "longest_trip": float(row[4] or 0),
    }