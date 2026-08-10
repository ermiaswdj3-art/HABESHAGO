"""
HABESHAGO Mini App Canonical Ride Reference Loader

Loads and validates one authoritative HABESHAGO ride
before exposing its identity to the Mini App.

The Mini App never treats a caller-supplied ride ID as
authoritative without verifying it against the shared
Ride Platform.
"""

from app.database.database import (
    create_connection,
)

from app.mini_app.ride_integration.models import (
    MiniAppCanonicalRideReference,
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


def load_canonical_ride_reference(
    ride_id: int,
) -> MiniAppCanonicalRideReference:
    """
    Load one canonical HABESHAGO ride identity.

    The shared rides table is authoritative.

    Raises:
        ValueError:
            If ride_id is invalid or the ride does not exist.
    """

    _require_positive_integer(
        ride_id,
        field_name="ride_id",
    )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                passenger_id,
                driver_id
            FROM rides
            WHERE id = ?
            """,
            (
                ride_id,
            ),
        )

        row = cursor.fetchone()

    finally:
        connection.close()

    if row is None:
        raise ValueError(
            "Ride not found."
        )

    return MiniAppCanonicalRideReference(
        ride_id=int(
            row[0]
        ),
        passenger_id=int(
            row[1]
        ),
        driver_id=int(
            row[2]
        ),
    )