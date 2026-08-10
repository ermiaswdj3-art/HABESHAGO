"""
HABESHAGO Ride Commerce Context Loader

Loads the canonical operational facts required to enter
the Ride Commerce Platform.

Authority:
- ride identity and passenger identity come from rides;
- payment method comes from the accepted Ride Offer that
  created the ride.

The loader does not:
- calculate fares
- calculate commission
- calculate driver earnings
- determine payment amounts
- execute Pricing
- execute Payment
- modify ride state
"""

from app.database.database import (
    create_connection,
)

from app.ride_commerce.context import (
    RideCommerceContext,
)


def _require_positive_integer(
    value: int,
    *,
    field_name: str,
) -> None:
    """
    Require one positive integer identifier.
    """

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value <= 0
    ):
        raise ValueError(
            f"{field_name} must be a positive integer."
        )


def load_ride_commerce_context(
    ride_id: int,
) -> RideCommerceContext:
    """
    Load the canonical Ride Commerce context for one ride.

    The ride must exist.

    Exactly one accepted Ride Offer must reference the
    ride so the passenger-selected payment method has one
    unambiguous operational authority.
    """

    _require_positive_integer(
        ride_id,
        field_name="ride_id",
    )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        # ==========================================
        # CANONICAL RIDE
        # ==========================================

        cursor.execute(
            """
            SELECT
                passenger_id
            FROM rides
            WHERE id = ?
            """,
            (
                ride_id,
            ),
        )

        ride_row = cursor.fetchone()

        if ride_row is None:
            raise ValueError(
                "Ride not found."
            )

        passenger_id = int(
            ride_row[0]
        )

        # ==========================================
        # ACCEPTED RIDE OFFER
        # ==========================================

        cursor.execute(
            """
            SELECT
                payment_method
            FROM ride_offers
            WHERE accepted_ride_id = ?
            ORDER BY id ASC
            """,
            (
                ride_id,
            ),
        )

        offer_rows = cursor.fetchall()

        if not offer_rows:
            raise ValueError(
                (
                    "Ride Commerce requires the "
                    "accepted Ride Offer that created "
                    "the ride."
                )
            )

        if len(
            offer_rows
        ) != 1:
            raise ValueError(
                (
                    "Ride Commerce requires exactly "
                    "one accepted Ride Offer for the "
                    "ride."
                )
            )

        payment_method = str(
            offer_rows[0][0]
        ).strip()

        # ==========================================
        # CANONICAL CONTEXT
        # ==========================================

        return RideCommerceContext(
            ride_id=ride_id,
            passenger_id=passenger_id,
            payment_method=payment_method,
        )

    finally:
        connection.close()