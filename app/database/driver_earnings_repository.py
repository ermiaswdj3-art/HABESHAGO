from app.constants.ride_status import (
    TRIP_COMPLETED,
)

from app.database.database import (
    create_connection,
)


def get_driver_financial_summary(driver_id):
    """
    Return the driver's lifetime financial summary.

    Result:
        {
            "completed_rides": 0,
            "gross_fares": 0.0,
            "commission_paid": 0.0,
            "net_earnings": 0.0,
        }
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(fare), 0),
            COALESCE(SUM(commission_amount), 0),
            COALESCE(SUM(driver_earnings), 0)
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
            "gross_fares": 0.0,
            "commission_paid": 0.0,
            "net_earnings": 0.0,
        }

    return {
        "completed_rides": int(
            row[0] or 0
        ),
        "gross_fares": float(
            row[1] or 0
        ),
        "commission_paid": float(
            row[2] or 0
        ),
        "net_earnings": float(
            row[3] or 0
        ),
    }


def get_driver_today_summary(driver_id):
    """
    Return today's completed rides and earnings.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(driver_earnings), 0)
        FROM rides
        WHERE driver_id = ?
          AND status = ?
          AND DATE(created_at) = DATE('now', 'localtime')
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
            "net_earnings": 0.0,
        }

    return {
        "completed_rides": int(
            row[0] or 0
        ),
        "net_earnings": float(
            row[1] or 0
        ),
    }


def get_driver_week_summary(driver_id):
    """
    Return completed rides and earnings
    from the last seven calendar days.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(driver_earnings), 0)
        FROM rides
        WHERE driver_id = ?
          AND status = ?
          AND DATE(created_at) >= DATE(
              'now',
              'localtime',
              '-6 days'
          )
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
            "net_earnings": 0.0,
        }

    return {
        "completed_rides": int(
            row[0] or 0
        ),
        "net_earnings": float(
            row[1] or 0
        ),
    }


def get_driver_month_summary(driver_id):
    """
    Return completed rides and earnings
    for the current calendar month.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            COALESCE(SUM(driver_earnings), 0)
        FROM rides
        WHERE driver_id = ?
          AND status = ?
          AND STRFTIME(
              '%Y-%m',
              created_at
          ) = STRFTIME(
              '%Y-%m',
              'now',
              'localtime'
          )
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
            "net_earnings": 0.0,
        }

    return {
        "completed_rides": int(
            row[0] or 0
        ),
        "net_earnings": float(
            row[1] or 0
        ),
    }