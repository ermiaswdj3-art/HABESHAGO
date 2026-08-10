"""
HABESHAGO Mini App Ride Integration Service

Coordinates the safe binding of one Mini App Trip to
one authoritative HABESHAGO Ride.

Responsibilities:
- validate the Mini App Trip;
- load the canonical Ride from the shared Ride Platform;
- bind the verified Ride identity to the Mini App Trip;
- return the verified canonical reference.

This service does not:
- create rides;
- accept ride offers;
- perform dispatch;
- calculate fares;
- process payments;
- modify canonical Ride state.
"""

from dataclasses import dataclass

from app.mini_app.models import (
    Trip,
)

from app.mini_app.ride_integration.binder import (
    bind_canonical_ride_reference,
)

from app.mini_app.ride_integration.models import (
    MiniAppCanonicalRideReference,
)

from app.mini_app.ride_integration.reference_loader import (
    load_canonical_ride_reference,
)


@dataclass(frozen=True)
class MiniAppRideIntegrationResult:
    """
    Result returned after one Mini App Trip has been
    safely attached to an authoritative HABESHAGO Ride.
    """

    trip: Trip
    reference: MiniAppCanonicalRideReference


def attach_trip_to_canonical_ride(
    *,
    trip: Trip,
    ride_id: int,
) -> MiniAppRideIntegrationResult:
    """
    Verify one canonical ride and bind its identity
    to the supplied Mini App Trip.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise ValueError(
            "trip must be a Trip."
        )

    reference = (
        load_canonical_ride_reference(
            ride_id
        )
    )

    bound_trip = (
        bind_canonical_ride_reference(
            trip=trip,
            reference=reference,
        )
    )

    return MiniAppRideIntegrationResult(
        trip=bound_trip,
        reference=reference,
    )