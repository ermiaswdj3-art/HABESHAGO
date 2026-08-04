"""
HABESHAGO Ride Settlement Repository

Provides persistent access to ride settlement records.
"""

from app.database.database import (
    create_connection,
)

from app.models import (
    RideSettlement,
)


def get_ride_settlement(
    ride_id: int,
) -> RideSettlement | None:
    """
    Return the settlement contract for one ride.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            driver_id,
            fare,
            service_type,
            commission_rate,
            commission_amount,
            driver_earnings,
            settlement_status,
            settled_at,
            settlement_reference
        FROM rides
        WHERE id = ?
        """,
        (ride_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return RideSettlement(
        ride_id=row[0],
        driver_id=row[1],
        fare=float(row[2] or 0),
        service_type=str(
            row[3] or "fuel"
        ),
        commission_rate=float(
            row[4] or 0
        ),
        commission_amount=float(
            row[5] or 0
        ),
        driver_earnings=float(
            row[6] or 0
        ),
        settlement_status=str(
            row[7] or "not_settled"
        ),
        settled_at=row[8],
        settlement_reference=row[9],
    )


def get_driver_settlements(
    driver_id: int,
    limit: int = 50,
) -> list[RideSettlement]:
    """
    Return recent settlements for one driver.
    """

    safe_limit = max(
        1,
        min(int(limit), 200),
    )

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            driver_id,
            fare,
            service_type,
            commission_rate,
            commission_amount,
            driver_earnings,
            settlement_status,
            settled_at,
            settlement_reference
        FROM rides
        WHERE driver_id = ?
          AND settlement_status = 'settled'
        ORDER BY settled_at DESC, id DESC
        LIMIT ?
        """,
        (
            driver_id,
            safe_limit,
        ),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        RideSettlement(
            ride_id=row[0],
            driver_id=row[1],
            fare=float(row[2] or 0),
            service_type=str(
                row[3] or "fuel"
            ),
            commission_rate=float(
                row[4] or 0
            ),
            commission_amount=float(
                row[5] or 0
            ),
            driver_earnings=float(
                row[6] or 0
            ),
            settlement_status=str(
                row[7] or "not_settled"
            ),
            settled_at=row[8],
            settlement_reference=row[9],
        )
        for row in rows
    ]