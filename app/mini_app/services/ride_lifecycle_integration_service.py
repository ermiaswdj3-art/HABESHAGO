"""
HABESHAGO Mini App Canonical Ride Lifecycle Integration

Connects an already-bound Mini App Trip to the
authoritative HABESHAGO Ride Transition Platform.

Commit #103 purpose:

- require an existing canonical Ride identity;
- require the canonical driver identity bound in #102;
- route lifecycle changes through transition_ride();
- prevent the Mini App from independently redefining
  authoritative Ride state;
- project successfully applied canonical Ride state into
  the Mini App presentation lifecycle;
- return one verified lifecycle result.

This service does not:

- create rides;
- create or accept Ride Offers;
- calculate fares;
- process payments;
- directly update the Ride database;
- publish duplicate lifecycle events.

The shared Ride Transition Service remains authoritative.
"""

from dataclasses import dataclass

from app.constants.ride_states import (
    RideState,
)

from app.mini_app.models import (
    Trip,
)

from app.services.ride_transition_service import (
    transition_ride,
)


class MiniAppCanonicalRideLifecycleError(
    ValueError
):
    """
    Raised when the Mini App cannot safely perform
    a canonical Ride lifecycle transition.
    """


@dataclass(frozen=True)
class MiniAppCanonicalRideLifecycleResult:
    """
    Result of one authoritative canonical Ride
    lifecycle transition and presentation projection.
    """

    trip: Trip

    ride_id: int
    driver_id: int

    previous_presentation_status: str
    canonical_state: str
    presentation_status: str


_CANONICAL_PRESENTATION_STATUS = {
    RideState.DRIVER_EN_ROUTE: (
        "driver_arriving"
    ),
    RideState.DRIVER_ARRIVED: (
        "driver_arrived"
    ),
    RideState.PASSENGER_ON_BOARD: (
        "ready_to_start"
    ),
    RideState.TRIP_STARTED: (
        "trip_in_progress"
    ),
    RideState.TRIP_COMPLETED: (
        "trip_completed"
    ),
}


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
        raise MiniAppCanonicalRideLifecycleError(
            (
                f"{field_name} must be a "
                "positive integer."
            )
        )

    return value


def _require_bound_canonical_trip(
    trip: Trip,
) -> tuple[int, int]:
    """
    Require a Mini App Trip already bound to one
    authoritative HABESHAGO Ride and driver.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppCanonicalRideLifecycleError(
            "trip must be a Trip."
        )

    ride_id = _require_positive_integer(
        trip.canonical_ride_id,
        field_name="canonical_ride_id",
    )

    driver_id = _require_positive_integer(
        trip.canonical_driver_id,
        field_name="canonical_driver_id",
    )

    assigned_driver_id = (
        trip.assigned_driver_id
    )

    if assigned_driver_id is not None:
        assigned_driver_id = (
            _require_positive_integer(
                assigned_driver_id,
                field_name=(
                    "assigned_driver_id"
                ),
            )
        )

        if (
            assigned_driver_id
            != driver_id
        ):
            raise (
                MiniAppCanonicalRideLifecycleError(
                    (
                        "Mini App assigned driver does "
                        "not match the canonical Ride "
                        "driver identity."
                    )
                )
            )

    return (
        ride_id,
        driver_id,
    )


def get_presentation_status_for_canonical_state(
    canonical_state: str,
) -> str:
    """
    Return the Mini App presentation state corresponding
    to one supported canonical Ride lifecycle state.

    Mini App workflow-only states such as
    pickup_verification_pending remain outside this
    canonical projection boundary.
    """

    presentation_status = (
        _CANONICAL_PRESENTATION_STATUS.get(
            canonical_state
        )
    )

    if presentation_status is None:
        raise MiniAppCanonicalRideLifecycleError(
            (
                "Canonical Ride state has no supported "
                "Mini App presentation projection: "
                f"{canonical_state}"
            )
        )

    return presentation_status


def project_canonical_state_to_trip(
    *,
    trip: Trip,
    canonical_state: str,
) -> str:
    """
    Project one successfully applied canonical Ride state
    into the Mini App presentation lifecycle.

    This function must be called only after the canonical
    Ride Platform has accepted and persisted the state.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppCanonicalRideLifecycleError(
            "trip must be a Trip."
        )

    presentation_status = (
        get_presentation_status_for_canonical_state(
            canonical_state
        )
    )

    try:
        trip.set_booking_status(
            presentation_status
        )

    except ValueError as exc:
        raise (
            MiniAppCanonicalRideLifecycleError(
                str(exc)
            )
        ) from exc

    return presentation_status


def transition_canonical_trip(
    *,
    trip: Trip,
    next_state: str,
) -> MiniAppCanonicalRideLifecycleResult:
    """
    Transition the authoritative Ride attached to one
    Mini App Trip and then project canonical truth into
    Mini App presentation state.

    The shared Ride Transition Service performs:

    - current-state loading;
    - transition validation;
    - database persistence;
    - active Ride synchronization;
    - platform event publication.

    Only after that canonical operation succeeds does this
    service update Mini App presentation state.
    """

    if (
        not isinstance(next_state, str)
        or not next_state.strip()
    ):
        raise MiniAppCanonicalRideLifecycleError(
            "next_state must be a non-empty string."
        )

    (
        ride_id,
        driver_id,
    ) = _require_bound_canonical_trip(
        trip
    )

    previous_presentation_status = (
        trip.booking_status
    )

    # Resolve the projection before changing canonical
    # state so unsupported states cannot partially apply
    # through this Mini App boundary.
    expected_presentation_status = (
        get_presentation_status_for_canonical_state(
            next_state
        )
    )

    try:
        canonical_state = transition_ride(
            ride_id=ride_id,
            driver_id=driver_id,
            next_state=next_state,
        )

    except ValueError as exc:
        raise (
            MiniAppCanonicalRideLifecycleError(
                str(exc)
            )
        ) from exc

    if canonical_state != next_state:
        raise MiniAppCanonicalRideLifecycleError(
            (
                "Canonical Ride transition returned "
                "an unexpected state."
            )
        )

    presentation_status = (
        project_canonical_state_to_trip(
            trip=trip,
            canonical_state=canonical_state,
        )
    )

    if (
        presentation_status
        != expected_presentation_status
    ):
        raise MiniAppCanonicalRideLifecycleError(
            (
                "Mini App lifecycle projection returned "
                "an unexpected presentation state."
            )
        )

    return MiniAppCanonicalRideLifecycleResult(
        trip=trip,
        ride_id=ride_id,
        driver_id=driver_id,
        previous_presentation_status=(
            previous_presentation_status
        ),
        canonical_state=canonical_state,
        presentation_status=(
            presentation_status
        ),
    )


def mark_driver_en_route(
    *,
    trip: Trip,
) -> MiniAppCanonicalRideLifecycleResult:
    """
    Transition the canonical Ride into driver en route.
    """

    return transition_canonical_trip(
        trip=trip,
        next_state=RideState.DRIVER_EN_ROUTE,
    )


def mark_driver_arrived(
    *,
    trip: Trip,
) -> MiniAppCanonicalRideLifecycleResult:
    """
    Transition the canonical Ride into driver arrived.
    """

    return transition_canonical_trip(
        trip=trip,
        next_state=RideState.DRIVER_ARRIVED,
    )


def mark_passenger_on_board(
    *,
    trip: Trip,
) -> MiniAppCanonicalRideLifecycleResult:
    """
    Transition the canonical Ride into passenger
    on-board state.
    """

    return transition_canonical_trip(
        trip=trip,
        next_state=(
            RideState.PASSENGER_ON_BOARD
        ),
    )


def mark_trip_started(
    *,
    trip: Trip,
) -> MiniAppCanonicalRideLifecycleResult:
    """
    Transition the canonical Ride into trip started.
    """

    return transition_canonical_trip(
        trip=trip,
        next_state=RideState.TRIP_STARTED,
    )


def mark_trip_completed(
    *,
    trip: Trip,
) -> MiniAppCanonicalRideLifecycleResult:
    """
    Transition the canonical Ride into trip completed.
    """

    return transition_canonical_trip(
        trip=trip,
        next_state=RideState.TRIP_COMPLETED,
    )