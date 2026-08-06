"""
HABESHAGO Admin Operations Repository

Provides canonical platform-wide operational counts for
the shared Admin Operations Platform.

This repository reports unique platform records—not
separate Telegram Bot or Mini App totals.
"""

from app.constants.offer_status import (
    ACCEPTED as OFFER_ACCEPTED,
    CANCELLED as OFFER_CANCELLED,
    EXPIRED as OFFER_EXPIRED,
    PENDING as OFFER_PENDING,
    REJECTED as OFFER_REJECTED,
)

from app.constants.ride_status import (
    ACCEPTED,
    CANCELLED,
    DRIVER_ARRIVED,
    DRIVER_ARRIVING,
    EXPIRED,
    RATED,
    REQUESTED,
    TRIP_COMPLETED,
    TRIP_STARTED,
)

from app.database.database import (
    create_connection,
)


ACTIVE_RIDE_STATUSES = (
    ACCEPTED,
    DRIVER_ARRIVING,
    DRIVER_ARRIVED,
    TRIP_STARTED,
)


def _count_query(
    cursor,
    query: str,
    parameters: tuple = (),
) -> int:
    """
    Execute one COUNT query and return a safe integer.
    """

    cursor.execute(
        query,
        parameters,
    )

    row = cursor.fetchone()

    if row is None:
        return 0

    return int(
        row[0] or 0
    )


def get_passenger_operations_summary() -> dict:
    """
    Return canonical passenger totals.
    """

    connection = create_connection()
    cursor = connection.cursor()

    total_passengers = _count_query(
        cursor,
        """
        SELECT COUNT(*)
        FROM passengers
        """,
    )

    connection.close()

    return {
        "total": total_passengers,
    }


def get_driver_registration_summary() -> dict:
    """
    Return the driver-registration lifecycle breakdown.
    """

    connection = create_connection()
    cursor = connection.cursor()

    summary = {
        "total": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            """,
        ),
        "approved": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            WHERE registration_status = 'approved'
            """,
        ),
        "verification_pending": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            WHERE registration_status =
                'verification_pending'
            """,
        ),
        "rejected": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            WHERE registration_status = 'rejected'
            """,
        ),
        "suspended": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            WHERE registration_status = 'suspended'
            """,
        ),
    }

    connection.close()

    return summary


def get_driver_operations_summary() -> dict:
    """
    Return the canonical operational-state breakdown.
    """

    connection = create_connection()
    cursor = connection.cursor()

    summary = {
        "online": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            WHERE is_online = 1
            """,
        ),
        "available": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            WHERE operational_status = 'available'
            """,
        ),
        "unavailable": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            WHERE operational_status = 'unavailable'
            """,
        ),
        "offline": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM drivers
            WHERE operational_status = 'offline'
            """,
        ),
    }

    connection.close()

    return summary


def get_ride_operations_summary() -> dict:
    """
    Return canonical ride-lifecycle totals.

    Today's metrics use lifecycle timestamps rather than
    treating each client as a separate ride source.
    """

    connection = create_connection()
    cursor = connection.cursor()

    active_placeholders = ", ".join(
        "?"
        for _ in ACTIVE_RIDE_STATUSES
    )

    summary = {
        "total": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            """,
        ),
        "requested": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status = ?
            """,
            (REQUESTED,),
        ),
        "active": _count_query(
            cursor,
            f"""
            SELECT COUNT(*)
            FROM rides
            WHERE status IN (
                {active_placeholders}
            )
            """,
            ACTIVE_RIDE_STATUSES,
        ),
        "completed": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status IN (?, ?)
            """,
            (
                TRIP_COMPLETED,
                RATED,
            ),
        ),
        "cancelled": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status = ?
            """,
            (CANCELLED,),
        ),
        "expired": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status = ?
            """,
            (EXPIRED,),
        ),
        "completed_today": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status IN (?, ?)
              AND DATE(
                    COALESCE(
                        completed_at,
                        created_at
                    )
                  ) = DATE(
                    'now',
                    'localtime'
                  )
            """,
            (
                TRIP_COMPLETED,
                RATED,
            ),
        ),
        "cancelled_today": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status = ?
              AND DATE(
                    COALESCE(
                        cancelled_at,
                        created_at
                    )
                  ) = DATE(
                    'now',
                    'localtime'
                  )
            """,
            (CANCELLED,),
        ),
        "expired_today": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status = ?
              AND DATE(
                    COALESCE(
                        expired_at,
                        created_at
                    )
                  ) = DATE(
                    'now',
                    'localtime'
                  )
            """,
            (EXPIRED,),
        ),
    }

    connection.close()

    return summary


def get_ride_offer_operations_summary() -> dict:
    """
    Return canonical Ride Offer lifecycle totals.
    """

    connection = create_connection()
    cursor = connection.cursor()

    summary = {
        "total": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM ride_offers
            """,
        ),
        "pending": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM ride_offers
            WHERE status = ?
              AND DATETIME(expires_at) >
                  DATETIME('now')
            """,
            (OFFER_PENDING,),
        ),
        "accepted": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM ride_offers
            WHERE status = ?
            """,
            (OFFER_ACCEPTED,),
        ),
        "rejected": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM ride_offers
            WHERE status = ?
            """,
            (OFFER_REJECTED,),
        ),
        "expired": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM ride_offers
            WHERE status = ?
               OR (
                    status = ?
                    AND DATETIME(expires_at) <=
                        DATETIME('now')
               )
            """,
            (
                OFFER_EXPIRED,
                OFFER_PENDING,
            ),
        ),
        "cancelled": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM ride_offers
            WHERE status = ?
            """,
            (OFFER_CANCELLED,),
        ),
    }

    connection.close()

    return summary


def get_settlement_operations_summary() -> dict:
    """
    Return settlement totals for completed rides only.

    Cancelled, requested, and active rides are excluded
    from financial exception reporting.
    """

    connection = create_connection()
    cursor = connection.cursor()

    completed_statuses = (
        TRIP_COMPLETED,
        RATED,
    )

    summary = {
        "completed_rides": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status IN (?, ?)
            """,
            completed_statuses,
        ),
        "settled": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status IN (?, ?)
              AND settlement_status = 'settled'
            """,
            completed_statuses,
        ),
        "not_settled": _count_query(
            cursor,
            """
            SELECT COUNT(*)
            FROM rides
            WHERE status IN (?, ?)
              AND settlement_status =
                  'not_settled'
            """,
            completed_statuses,
        ),
        "gross_fares": 0.0,
        "commission": 0.0,
        "driver_earnings": 0.0,
    }

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(fare), 0),
            COALESCE(
                SUM(commission_amount),
                0
            ),
            COALESCE(
                SUM(driver_earnings),
                0
            )
        FROM rides
        WHERE status IN (?, ?)
          AND settlement_status = 'settled'
        """,
        completed_statuses,
    )

    financial_row = cursor.fetchone()

    connection.close()

    if financial_row is not None:
        summary["gross_fares"] = float(
            financial_row[0] or 0
        )

        summary["commission"] = float(
            financial_row[1] or 0
        )

        summary["driver_earnings"] = float(
            financial_row[2] or 0
        )

    return summary