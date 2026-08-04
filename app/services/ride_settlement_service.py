"""
HABESHAGO Ride Settlement Service

Finalizes the financial settlement of a completed ride.

The service guarantees that:
- only valid rides can be settled;
- settlement is idempotent;
- earnings are recalculated from authoritative ride data;
- financial values and lifecycle completion are persisted
  together in one database transaction.
"""

from datetime import datetime, timezone
from secrets import token_hex

from app.constants.ride_status import (
    TRIP_COMPLETED,
)

from app.database.database import (
    create_connection,
)

from app.models import (
    RideSettlement,
)

from app.services.earnings_service import (
    calculate_earnings,
)


def _generate_settlement_reference() -> str:
    """
    Generate a unique settlement reference.
    """

    date_code = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d")

    random_code = token_hex(
        5
    ).upper()

    return (
        f"SET-{date_code}-{random_code}"
    )


def settle_completed_ride(
    ride_id: int,
) -> RideSettlement:
    """
    Finalize one ride financially and operationally.

    The operation is idempotent. If the ride is already
    settled, the existing settlement is returned without
    charging commission again.
    """

    if ride_id <= 0:
        raise ValueError(
            "ride_id must be greater than zero."
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor.execute(
            """
            SELECT
                id,
                driver_id,
                fare,
                service_type,
                status,
                settlement_status,
                settled_at,
                settlement_reference,
                commission_rate,
                commission_amount,
                driver_earnings
            FROM rides
            WHERE id = ?
            """,
            (ride_id,),
        )

        ride = cursor.fetchone()

        if ride is None:
            raise ValueError(
                "Ride not found."
            )

        (
            stored_ride_id,
            driver_id,
            fare,
            service_type,
            ride_status,
            settlement_status,
            settled_at,
            settlement_reference,
            stored_commission_rate,
            stored_commission_amount,
            stored_driver_earnings,
        ) = ride

        if settlement_status == "settled":
            settlement = RideSettlement(
                ride_id=stored_ride_id,
                driver_id=driver_id,
                fare=float(fare or 0),
                service_type=str(
                    service_type or "fuel"
                ),
                commission_rate=float(
                    stored_commission_rate or 0
                ),
                commission_amount=float(
                    stored_commission_amount or 0
                ),
                driver_earnings=float(
                    stored_driver_earnings or 0
                ),
                settlement_status="settled",
                settled_at=settled_at,
                settlement_reference=(
                    settlement_reference
                ),
            )

            settlement.validate()

            return settlement

        if ride_status not in {
            "TRIP_STARTED",
            TRIP_COMPLETED,
        }:
            raise ValueError(
                "Only a started or completed trip "
                "can be settled."
            )

        earnings = calculate_earnings(
            float(fare or 0),
            str(service_type or "fuel"),
        )

        settlement_reference = (
            _generate_settlement_reference()
        )

        cursor.execute(
            """
            UPDATE rides
            SET
                commission_rate = ?,
                commission_amount = ?,
                driver_earnings = ?,

                settlement_status = 'settled',
                settled_at = CURRENT_TIMESTAMP,
                settlement_reference = ?,

                status = ?,
                completed_at = COALESCE(
                    completed_at,
                    CURRENT_TIMESTAMP
                )
            WHERE id = ?
              AND settlement_status != 'settled'
            """,
            (
                earnings["commission_rate"],
                earnings["commission_amount"],
                earnings["driver_earnings"],
                settlement_reference,
                TRIP_COMPLETED,
                ride_id,
            ),
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                "Ride settlement could not be persisted."
            )

        cursor.execute(
            """
            SELECT
                settled_at
            FROM rides
            WHERE id = ?
            """,
            (ride_id,),
        )

        settled_row = cursor.fetchone()

        connection.commit()

        settlement = RideSettlement(
            ride_id=stored_ride_id,
            driver_id=driver_id,
            fare=earnings["fare"],
            service_type=str(
                service_type or "fuel"
            ),
            commission_rate=(
                earnings["commission_rate"]
            ),
            commission_amount=(
                earnings["commission_amount"]
            ),
            driver_earnings=(
                earnings["driver_earnings"]
            ),
            settlement_status="settled",
            settled_at=(
                settled_row[0]
                if settled_row
                else None
            ),
            settlement_reference=(
                settlement_reference
            ),
        )

        settlement.validate()

        return settlement

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()