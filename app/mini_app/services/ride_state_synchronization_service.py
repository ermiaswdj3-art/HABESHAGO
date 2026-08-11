"""
HABESHAGO Mini App Canonical Ride State Synchronization

Synchronizes an already-bound Mini App Trip with the
authoritative HABESHAGO Ride state stored by the platform.

Commit #104 purpose:

- require an existing canonical Ride identity;
- verify canonical Ride, passenger, and driver identity;
- read the authoritative Ride state;
- reuse the #103 canonical-to-presentation projection;
- reconcile stale Mini App lifecycle state;
- report whether synchronization changed presentation state.

This service does not:

- create rides;
- transition canonical Ride state;
- update the Ride database;
- publish lifecycle events;
- process dispatch, pricing, or payments.

The canonical Ride Platform remains authoritative.
"""

from dataclasses import dataclass

from app.database.ride_repository import (
    get_ride_status,
)

from app.mini_app.models import (
    Trip,
)

from app.mini_app.ride_integration.reference_loader import (
    load_canonical_ride_reference,
)

from app.mini_app.services.ride_lifecycle_integration_service import (
    MiniAppCanonicalRideLifecycleError,
    get_presentation_status_for_canonical_state,
    project_canonical_state_to_trip,
)


class MiniAppRideStateSynchronizationError(
    ValueError
):
    """
    Raised when the Mini App cannot safely synchronize
    with the authoritative Ride lifecycle.
    """


@dataclass(frozen=True)
class MiniAppRideStateSynchronizationResult:
    """
    Result of one authoritative Ride-state synchronization.
    """

    trip: Trip

    ride_id: int
    passenger_id: int
    driver_id: int

    canonical_state: str
    previous_presentation_status: str
    presentation_status: str

    synchronized: bool


def _require_positive_integer(
    value,
    *,
    field_name: str,
) -> int:
    """
    Require one positive integer identifier.
    """

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
    ):
        raise MiniAppRideStateSynchronizationError(
            (
                f"{field_name} must be a "
                "positive integer."
            )
        )

    return value


def _require_bound_trip(
    trip: Trip,
) -> tuple[int, int, int]:
    """
    Require a Mini App Trip already bound to one
    authoritative HABESHAGO Ride and its actors.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppRideStateSynchronizationError(
            "trip must be a Trip."
        )

    ride_id = _require_positive_integer(
        trip.canonical_ride_id,
        field_name="canonical_ride_id",
    )

    passenger_id = _require_positive_integer(
        trip.canonical_passenger_id,
        field_name="canonical_passenger_id",
    )

    driver_id = _require_positive_integer(
        trip.canonical_driver_id,
        field_name="canonical_driver_id",
    )

    return (
        ride_id,
        passenger_id,
        driver_id,
    )


def _verify_canonical_ride_identity(
    *,
    ride_id: int,
    passenger_id: int,
    driver_id: int,
) -> None:
    """
    Verify that Mini App canonical identities match
    the authoritative shared Ride record.
    """

    try:
        reference = (
            load_canonical_ride_reference(
                ride_id
            )
        )

    except ValueError as exc:
        raise (
            MiniAppRideStateSynchronizationError(
                str(exc)
            )
        ) from exc

    if reference.ride_id != ride_id:
        raise MiniAppRideStateSynchronizationError(
            (
                "Canonical Ride identity does not "
                "match the Mini App Trip."
            )
        )

    if reference.passenger_id != passenger_id:
        raise MiniAppRideStateSynchronizationError(
            (
                "Canonical passenger identity does "
                "not match the Mini App Trip."
            )
        )

    if reference.driver_id != driver_id:
        raise MiniAppRideStateSynchronizationError(
            (
                "Canonical driver identity does not "
                "match the Mini App Trip."
            )
        )


def load_authoritative_ride_state(
    *,
    trip: Trip,
) -> tuple[int, int, int, str]:
    """
    Load the authoritative lifecycle state for the
    canonical Ride attached to one Mini App Trip.

    Canonical Ride identity is verified before the
    lifecycle state is exposed to the Mini App.
    """

    (
        ride_id,
        passenger_id,
        driver_id,
    ) = _require_bound_trip(
        trip
    )

    _verify_canonical_ride_identity(
        ride_id=ride_id,
        passenger_id=passenger_id,
        driver_id=driver_id,
    )

    canonical_state = get_ride_status(
        ride_id
    )

    if canonical_state is None:
        raise MiniAppRideStateSynchronizationError(
            "Canonical Ride not found."
        )

    try:
        get_presentation_status_for_canonical_state(
            canonical_state
        )

    except MiniAppCanonicalRideLifecycleError as exc:
        raise (
            MiniAppRideStateSynchronizationError(
                str(exc)
            )
        ) from exc

    return (
        ride_id,
        passenger_id,
        driver_id,
        canonical_state,
    )


def synchronize_trip_with_canonical_ride(
    *,
    trip: Trip,
) -> MiniAppRideStateSynchronizationResult:
    """
    Reconcile one Mini App Trip with authoritative
    canonical Ride lifecycle state.

    Canonical state is read only.

    The Mini App presentation state changes only when
    it differs from the canonical projection.
    """

    (
        ride_id,
        passenger_id,
        driver_id,
        canonical_state,
    ) = load_authoritative_ride_state(
        trip=trip
    )

    previous_presentation_status = (
        trip.booking_status
    )

    try:
        presentation_status = (
            get_presentation_status_for_canonical_state(
                canonical_state
            )
        )

    except MiniAppCanonicalRideLifecycleError as exc:
        raise (
            MiniAppRideStateSynchronizationError(
                str(exc)
            )
        ) from exc

    synchronized = (
        previous_presentation_status
        != presentation_status
    )

    if synchronized:
        try:
            presentation_status = (
                project_canonical_state_to_trip(
                    trip=trip,
                    canonical_state=canonical_state,
                )
            )

        except MiniAppCanonicalRideLifecycleError as exc:
            raise (
                MiniAppRideStateSynchronizationError(
                    str(exc)
                )
            ) from exc

    return MiniAppRideStateSynchronizationResult(
        trip=trip,
        ride_id=ride_id,
        passenger_id=passenger_id,
        driver_id=driver_id,
        canonical_state=canonical_state,
        previous_presentation_status=(
            previous_presentation_status
        ),
        presentation_status=presentation_status,
        synchronized=synchronized,
    )