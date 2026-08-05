"""
HABESHAGO Ride Offer Repository

Provides persistent access to canonical ride-offer records
and atomic lifecycle transitions.
"""

from app.constants.offer_status import (
    ACCEPTED,
    CANCELLED,
    EXPIRED,
    PENDING,
    REJECTED,
)

from app.database.database import (
    create_connection,
)

from app.models import (
    RideOffer,
)


def _row_to_ride_offer(
    row,
) -> RideOffer | None:
    """
    Convert one database row into a RideOffer model.
    """

    if row is None:
        return None

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
        status=str(
            row[15] or PENDING
        ),
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


def _select_offer_by_id(
    cursor,
    offer_id: int,
):
    """
    Load one offer row using an existing cursor.
    """

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

    return cursor.fetchone()


def create_ride_offer(
    offer_reference: str,
    passenger_id: int,
    driver_id: int,
    pickup_latitude: float,
    pickup_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
    distance: float,
    pickup_distance: float,
    pickup_eta: int,
    trip_eta: int,
    fare: float,
    payment_method: str = "Cash",
    service_type: str = "fuel",
    expiration_seconds: int = 30,
) -> RideOffer:
    """
    Create one persistent pending ride offer.
    """

    if expiration_seconds <= 0:
        raise ValueError(
            "expiration_seconds must be greater than zero."
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO ride_offers (
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
                expires_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?,
                DATETIME(
                    'now',
                    '+' || ? || ' seconds'
                )
            )
            """,
            (
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
                PENDING,
                expiration_seconds,
            ),
        )

        offer_id = cursor.lastrowid

        row = _select_offer_by_id(
            cursor,
            offer_id,
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    offer = _row_to_ride_offer(row)

    if offer is None:
        raise RuntimeError(
            "Ride offer could not be loaded after creation."
        )

    return offer


def get_ride_offer(
    offer_id: int,
) -> RideOffer | None:
    """
    Return one ride offer by ID.
    """

    connection = create_connection()
    cursor = connection.cursor()

    row = _select_offer_by_id(
        cursor,
        offer_id,
    )

    connection.close()

    return _row_to_ride_offer(row)


def get_pending_offer_for_driver(
    driver_id: int,
) -> RideOffer | None:
    """
    Return the driver's current pending offer.
    """

    connection = create_connection()
    cursor = connection.cursor()

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
        WHERE driver_id = ?
          AND status = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            driver_id,
            PENDING,
        ),
    )

    row = cursor.fetchone()

    connection.close()

    return _row_to_ride_offer(row)


def get_pending_offer_for_passenger(
    passenger_id: int,
) -> RideOffer | None:
    """
    Return the passenger's current pending offer.
    """

    connection = create_connection()
    cursor = connection.cursor()

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
        WHERE passenger_id = ?
          AND status = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            passenger_id,
            PENDING,
        ),
    )

    row = cursor.fetchone()

    connection.close()

    return _row_to_ride_offer(row)


def accept_ride_offer(
    offer_id: int,
    accepted_ride_id: int,
) -> RideOffer:
    """
    Atomically transition PENDING → ACCEPTED.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
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
                ACCEPTED,
                accepted_ride_id,
                offer_id,
                PENDING,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "Ride offer is no longer available "
                "for acceptance."
            )

        row = _select_offer_by_id(
            cursor,
            offer_id,
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    offer = _row_to_ride_offer(row)

    if offer is None:
        raise RuntimeError(
            "Accepted ride offer could not be loaded."
        )

    return offer


def reject_ride_offer(
    offer_id: int,
) -> RideOffer:
    """
    Atomically transition PENDING → REJECTED.
    """

    return _transition_pending_offer(
        offer_id=offer_id,
        target_status=REJECTED,
        timestamp_column="rejected_at",
    )


def expire_ride_offer(
    offer_id: int,
) -> RideOffer:
    """
    Atomically transition PENDING → EXPIRED.
    """

    return _transition_pending_offer(
        offer_id=offer_id,
        target_status=EXPIRED,
        timestamp_column="expired_at",
    )


def cancel_ride_offer(
    offer_id: int,
) -> RideOffer:
    """
    Atomically transition PENDING → CANCELLED.
    """

    return _transition_pending_offer(
        offer_id=offer_id,
        target_status=CANCELLED,
        timestamp_column="cancelled_at",
    )


def _transition_pending_offer(
    offer_id: int,
    target_status: str,
    timestamp_column: str,
) -> RideOffer:
    """
    Perform one trusted terminal transition.
    """

    allowed_transitions = {
        REJECTED: "rejected_at",
        EXPIRED: "expired_at",
        CANCELLED: "cancelled_at",
    }

    expected_column = allowed_transitions.get(
        target_status
    )

    if expected_column != timestamp_column:
        raise ValueError(
            "Invalid ride-offer transition."
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            f"""
            UPDATE ride_offers
            SET
                status = ?,
                {timestamp_column} = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status = ?
            """,
            (
                target_status,
                offer_id,
                PENDING,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "Ride offer is no longer pending."
            )

        row = _select_offer_by_id(
            cursor,
            offer_id,
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    offer = _row_to_ride_offer(row)

    if offer is None:
        raise RuntimeError(
            "Ride offer could not be loaded "
            "after transition."
        )

    return offer


def get_pending_offer_driver_ids() -> set[int]:
    """
    Return the IDs of drivers who currently hold
    non-expired pending ride offers.

    Overdue offers are excluded from this result.
    The Ride Offer Service or recovery process remains
    responsible for changing their status to EXPIRED.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT
            driver_id
        FROM ride_offers
        WHERE status = ?
          AND DATETIME(expires_at) >
              DATETIME('now')
        """,
        (PENDING,),
    )

    rows = cursor.fetchall()

    connection.close()

    return {
        int(row[0])
        for row in rows
    }

def get_all_pending_ride_offers() -> list[RideOffer]:
    """
    Return every currently pending ride offer.

    Expiration should be processed before calling
    this function during application recovery.
    """

    connection = create_connection()
    cursor = connection.cursor()

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
        WHERE status = ?
          AND DATETIME(expires_at) >
              DATETIME('now')
        ORDER BY id
        """,
        (PENDING,),
    )

    rows = cursor.fetchall()

    connection.close()

    offers = []

    for row in rows:
        offer = _row_to_ride_offer(
            row
        )

        if offer is not None:
            offers.append(
                offer
            )

    return offers

def expire_due_ride_offers() -> int:
    """
    Expire every pending offer whose deadline passed.

    Returns the number of offers expired.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE ride_offers
            SET
                status = ?,
                expired_at = CURRENT_TIMESTAMP
            WHERE status = ?
              AND DATETIME(expires_at) <=
                  DATETIME('now')
            """,
            (
                EXPIRED,
                PENDING,
            ),
        )

        expired_count = cursor.rowcount

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return expired_count