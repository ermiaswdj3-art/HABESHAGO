"""
HABESHAGO Mini App Ride Acceptance Adapter

Connects the shared Ride Offer Acceptance Platform
to Mini App presentation state.

The shared Ride Platform remains authoritative.

This adapter:
- receives an existing canonical acceptance result;
- validates its identity fields;
- reloads the canonical Ride from persistence;
- verifies that acceptance identity matches persistence;
- binds that canonical Ride to the Mini App Trip.

This adapter does not:
- accept ride offers;
- create rides;
- perform dispatch;
- calculate fares;
- process payments.
"""

from typing import Any

from app.mini_app.models import (
    Trip,
)

from app.mini_app.ride_integration.models import (
    MiniAppCanonicalRideReference,
)

from app.mini_app.ride_integration.service import (
    MiniAppRideIntegrationResult,
    attach_trip_to_canonical_ride,
)


def _require_positive_integer(
    value: Any,
    *,
    field_name: str,
) -> int:
    """
    Require and return one positive integer identifier.
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

    return value


def attach_trip_from_accepted_offer(
    *,
    trip: Trip,
    acceptance_result: dict[str, Any],
) -> MiniAppRideIntegrationResult:
    """
    Attach one Mini App Trip using the canonical result
    returned by Ride Offer acceptance.

    The acceptance result is not blindly trusted.

    Its ride_id is used to reload the authoritative Ride,
    and passenger/driver identity must exactly match the
    persisted canonical Ride.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise ValueError(
            "trip must be a Trip."
        )

    if not isinstance(
        acceptance_result,
        dict,
    ):
        raise ValueError(
            "acceptance_result must be a dict."
        )

    ride_id = _require_positive_integer(
        acceptance_result.get(
            "ride_id"
        ),
        field_name="ride_id",
    )

    passenger_id = _require_positive_integer(
        acceptance_result.get(
            "passenger_id"
        ),
        field_name="passenger_id",
    )

    driver_id = _require_positive_integer(
        acceptance_result.get(
            "driver_id"
        ),
        field_name="driver_id",
    )

    integration_result = (
        attach_trip_to_canonical_ride(
            trip=trip,
            ride_id=ride_id,
        )
    )

    authoritative_reference: (
        MiniAppCanonicalRideReference
    ) = integration_result.reference

    if (
        authoritative_reference.passenger_id
        != passenger_id
    ):
        raise ValueError(
            (
                "Accepted Ride passenger identity does "
                "not match the authoritative Ride."
            )
        )

    if (
        authoritative_reference.driver_id
        != driver_id
    ):
        raise ValueError(
            (
                "Accepted Ride driver identity does "
                "not match the authoritative Ride."
            )
        )

    return integration_result