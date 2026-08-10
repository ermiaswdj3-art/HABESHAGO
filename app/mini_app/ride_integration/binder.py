"""
HABESHAGO Mini App Canonical Ride Binder

Binds a verified authoritative Ride reference to the
Mini App's presentation-level Trip object.

The Mini App remains an interface and does not create
or redefine shared Ride Platform identity.
"""

from app.mini_app.models import (
    Trip,
)

from app.mini_app.ride_integration.models import (
    MiniAppCanonicalRideReference,
)


def bind_canonical_ride_reference(
    *,
    trip: Trip,
    reference: MiniAppCanonicalRideReference,
) -> Trip:
    """
    Attach one verified canonical Ride reference
    to the Mini App Trip.

    This function does not create, modify, or persist
    the authoritative Ride itself.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise ValueError(
            "trip must be a Trip."
        )

    if not isinstance(
        reference,
        MiniAppCanonicalRideReference,
    ):
        raise ValueError(
            (
                "reference must be a "
                "MiniAppCanonicalRideReference."
            )
        )

    trip.canonical_ride_id = (
        reference.ride_id
    )

    trip.canonical_passenger_id = (
        reference.passenger_id
    )

    trip.canonical_driver_id = (
        reference.driver_id
    )

    return trip