"""
HABESHAGO Ride Offer Acceptance Service

Atomically converts one valid pending Ride Offer into:

- one accepted Ride record;
- one accepted Ride Offer record linked to that ride.

Both changes succeed together or roll back together.
"""

from app.constants.offer_status import (
    ACCEPTED as OFFER_ACCEPTED,
    PENDING,
)

from app.constants.ride_status import (
    ACCEPTED as RIDE_ACCEPTED,
)

from app.database.database import (
    create_connection,
)

from app.models import (
    RideOffer,
)

from app.services.earnings_service import (
    calculate_earnings,
)


def _row_to_offer(
    row,
) -> RideOffer:
    """
    Convert the acceptance query result into a RideOffer.
    """

    if row is None:
        raise RuntimeError(
            "Accepted ride offer could not be loaded."
        )

    offer = RideOffer(
        offer_id=row[0],
        offer_reference=row[1],
        passenger_id=row[2],
        driver_id=row[3],
        pickup_latitude=float(row[4]),
        pickup_longitude=float(row[5]),
        destination_latitude=float(row[6]),
        destination_longitude=float(row[7]),
        distance=float(row[8]),
        pickup_distance=float(row[9]),
        pickup_eta=int(row[10]),
        trip_eta=int(row[11]),
        fare=float(row[12]),
        payment_method=str(
            row[13] or "Cash"
        ),
        service_type=str(
            row[14] or "fuel"
        ),
        status=str(row[15]),
        accepted_ride_id=row[16],
        created_at=row[17],
        expires_at=row[18],
        accepted_at=row[19],
        rejected_at=row[20],
        expired_at=row[21],
        cancelled_at=row[22],
    )

    offer.validate()

    return offer


def _serialize_acceptance(
    offer: RideOffer,
) -> dict:
    """
    Return the shared acceptance result contract.
    """

    return {
        "ride_id": offer.accepted_ride_id,
        "offer_id": offer.offer_id,
        "offer_reference": (
            offer.offer_reference
        ),
        "passenger_id": offer.passenger_id,
        "driver_id": offer.driver_id,
        "pickup": (
            offer.pickup_latitude,
            offer.pickup_longitude,
        ),
        "destination": (
            offer.destination_latitude,
            offer.destination_longitude,
        ),
        "distance": offer.distance,
        "pickup_distance": (
            offer.pickup_distance
        ),
        "pickup_eta": offer.pickup_eta,
        "trip_eta": offer.trip_eta,
        "fare": offer.fare,
        "payment_method": (
            offer.payment_method
        ),
        "service_type": offer.service_type,
        "offer_status": offer.status,
        "accepted_at": offer.accepted_at,
    }


def accept_offer_and_create_ride(
    offer_id: int,
    driver_id: int,
) -> dict:
    """
    Atomically accept one pending offer and create its ride.

    The driver ID must match the driver selected by the
    Dispatch Platform when the offer was created.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Use an immediate transaction so another writer
        # cannot accept or resolve this offer concurrently.
        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        cursor.execute(
            """
            SELECT
                id,
                offer_reference,
                passenger_id,
                driver_id,
                pickup_latitude,
                pickup_longitude,
                destination_latitude,
                destination_longitude,
                distance,
                pickup_distance,
                pickup_eta,
                trip_eta,
                fare,
                payment_method,
                service_type,
                status,
                accepted_ride_id,
                created_at,
                expires_at,
                accepted_at,
                rejected_at,
                expired_at,
                cancelled_at
            FROM ride_offers
            WHERE id = ?
            """,
            (offer_id,),
        )

        offer_row = cursor.fetchone()

        if offer_row is None:
            raise ValueError(
                "Ride offer was not found."
            )

        if offer_row[3] != driver_id:
            raise ValueError(
                "This ride offer belongs to another driver."
            )

        if offer_row[15] != PENDING:
            raise ValueError(
                "Ride offer is no longer pending."
            )

        cursor.execute(
            """
            SELECT
                CASE
                    WHEN DATETIME(?) >
                         DATETIME('now')
                    THEN 1
                    ELSE 0
                END
            """,
            (offer_row[18],),
        )

        expiration_result = cursor.fetchone()

        if (
            expiration_result is None
            or expiration_result[0] != 1
        ):
            cursor.execute(
                """
                UPDATE ride_offers
                SET
                    status = 'EXPIRED',
                    expired_at = CURRENT_TIMESTAMP
                WHERE id = ?
                  AND status = ?
                """,
                (
                    offer_id,
                    PENDING,
                ),
            )

            connection.commit()

            raise ValueError(
                "Ride offer has expired."
            )

        fare = float(offer_row[12])
        service_type = str(
            offer_row[14] or "fuel"
        )

        earnings = calculate_earnings(
            fare,
            service_type,
        )

        cursor.execute(
            """
            INSERT INTO rides (
                passenger_id,
                driver_id,
                pickup_latitude,
                pickup_longitude,
                destination_latitude,
                destination_longitude,
                distance,
                fare,
                service_type,
                commission_rate,
                commission_amount,
                driver_earnings,
                settlement_status,
                status,
                created_at,
                requested_at,
                accepted_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                'not_settled',
                ?,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """,
            (
                offer_row[2],
                offer_row[3],
                offer_row[4],
                offer_row[5],
                offer_row[6],
                offer_row[7],
                offer_row[8],
                earnings["fare"],
                service_type,
                earnings["commission_rate"],
                earnings["commission_amount"],
                earnings["driver_earnings"],
                RIDE_ACCEPTED,
            ),
        )

        ride_id = cursor.lastrowid

        cursor.execute(
            """
            UPDATE ride_offers
            SET
                status = ?,
                accepted_ride_id = ?,
                accepted_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status = ?
              AND DATETIME(expires_at) >
                  DATETIME('now')
            """,
            (
                OFFER_ACCEPTED,
                ride_id,
                offer_id,
                PENDING,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "Ride offer could not be accepted."
            )

        cursor.execute(
            """
            SELECT
                id,
                offer_reference,
                passenger_id,
                driver_id,
                pickup_latitude,
                pickup_longitude,
                destination_latitude,
                destination_longitude,
                distance,
                pickup_distance,
                pickup_eta,
                trip_eta,
                fare,
                payment_method,
                service_type,
                status,
                accepted_ride_id,
                created_at,
                expires_at,
                accepted_at,
                rejected_at,
                expired_at,
                cancelled_at
            FROM ride_offers
            WHERE id = ?
            """,
            (offer_id,),
        )

        accepted_row = cursor.fetchone()

        connection.commit()

    except ValueError:
        # A deliberately persisted EXPIRED transition
        # has already committed above.
        if connection.in_transaction:
            connection.rollback()

        raise

    except Exception:
        if connection.in_transaction:
            connection.rollback()

        raise

    finally:
        connection.close()

    accepted_offer = _row_to_offer(
        accepted_row
    )

    return _serialize_acceptance(
        accepted_offer
    )