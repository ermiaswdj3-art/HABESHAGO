"""
HABESHAGO Mini App Passenger Synchronization Recovery

Coordinates recovery of one authenticated passenger's
Mini App presentation state after synchronization
delivery interruption, reconnect, or stale client state.

Commit #107 purpose:

- recover from missed or delayed passenger updates;
- preserve the canonical Ride Platform as authority;
- reuse canonical Ride-state synchronization;
- expose pending passenger synchronization context;
- never trust passenger identity supplied by the browser;
- never transition canonical Ride state during recovery;
- never acknowledge synchronization updates automatically.

Recovery is orchestration only.

Canonical Ride state remains authoritative.
"""

from dataclasses import dataclass

from app.mini_app.models import (
    Trip,
)

from app.mini_app.services.ride_state_synchronization_service import (
    MiniAppRideStateSynchronizationError,
    synchronize_trip_with_canonical_ride,
)

from app.models.synchronization_update import (
    SynchronizationUpdate,
)

from app.services.synchronization_service import (
    get_pending_passenger_updates,
)


class MiniAppPassengerSynchronizationRecoveryError(
    ValueError
):
    """
    Raised when passenger synchronization recovery
    cannot be performed safely.
    """


@dataclass(frozen=True)
class MiniAppPassengerSynchronizationRecoveryResult:
    """
    Result of one passenger synchronization recovery.
    """

    trip: Trip

    passenger_id: int
    ride_id: int
    driver_id: int

    canonical_state: str

    previous_presentation_status: str
    presentation_status: str

    synchronized: bool

    pending_updates: tuple[
        SynchronizationUpdate,
        ...,
    ]


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
        raise MiniAppPassengerSynchronizationRecoveryError(
            (
                f"{field_name} must be a "
                "positive integer."
            )
        )

    return value


def recover_passenger_synchronization(
    *,
    trip: Trip,
    passenger_id: int,
) -> MiniAppPassengerSynchronizationRecoveryResult:
    """
    Recover one authenticated passenger's Mini App
    synchronization state.

    Passenger identity must match the canonical passenger
    already bound to the Mini App Trip.

    Recovery performs two independent reads:

    1. synchronize the Mini App presentation with the
       authoritative canonical Ride lifecycle;
    2. load pending synchronization updates belonging
       only to the authenticated passenger.

    Pending updates remain queued.

    Recovery never acknowledges updates and never
    transitions canonical Ride state.
    """

    authenticated_passenger_id = (
        _require_positive_integer(
            passenger_id,
            field_name="passenger_id",
        )
    )

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppPassengerSynchronizationRecoveryError(
            "trip must be a Trip."
        )

    canonical_passenger_id = (
        _require_positive_integer(
            trip.canonical_passenger_id,
            field_name="canonical_passenger_id",
        )
    )

    if (
        canonical_passenger_id
        != authenticated_passenger_id
    ):
        raise MiniAppPassengerSynchronizationRecoveryError(
            (
                "Authenticated passenger does not "
                "match the Mini App Trip."
            )
        )

    try:
        synchronization_result = (
            synchronize_trip_with_canonical_ride(
                trip=trip,
            )
        )
    except MiniAppRideStateSynchronizationError as exc:
        raise (
            MiniAppPassengerSynchronizationRecoveryError(
                str(exc)
            )
        ) from exc

    try:
        pending_updates = tuple(
            get_pending_passenger_updates(
                authenticated_passenger_id
            )
        )
    except ValueError as exc:
        raise (
            MiniAppPassengerSynchronizationRecoveryError(
                str(exc)
            )
        ) from exc

    return MiniAppPassengerSynchronizationRecoveryResult(
        trip=trip,
        passenger_id=authenticated_passenger_id,
        ride_id=synchronization_result.ride_id,
        driver_id=synchronization_result.driver_id,
        canonical_state=(
            synchronization_result.canonical_state
        ),
        previous_presentation_status=(
            synchronization_result
            .previous_presentation_status
        ),
        presentation_status=(
            synchronization_result.presentation_status
        ),
        synchronized=(
            synchronization_result.synchronized
        ),
        pending_updates=pending_updates,
    )
