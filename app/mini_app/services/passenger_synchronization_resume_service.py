"""
HABESHAGO Mini App Passenger Synchronization Resume Service

Builds one deterministic synchronization resume snapshot
for an authenticated HABESHAGO passenger.

Commit #112 purpose:

- compose canonical Ride recovery with passenger cursor state;
- replay only synchronization updates occurring after the
  passenger's last acknowledged synchronization sequence;
- expose one deterministic Mini App resume contract;
- preserve the canonical Ride Platform as authority;
- never trust passenger identity supplied by the browser;
- never acknowledge synchronization updates automatically;
- never advance the passenger synchronization cursor;
- never transition canonical Ride state.

Resume is orchestration only.

Acknowledgement remains the only operation that advances
trusted passenger synchronization progress.
"""

from dataclasses import dataclass

from app.mini_app.models import (
    Trip,
)

from app.mini_app.services.passenger_synchronization_recovery_service import (
    MiniAppPassengerSynchronizationRecoveryError,
    recover_passenger_synchronization,
)

from app.models.passenger_synchronization_cursor import (
    PassengerSynchronizationCursor,
)

from app.models.synchronization_update import (
    SynchronizationUpdate,
)

from app.services.synchronization_service import (
    get_passenger_synchronization_cursor,
    get_pending_passenger_updates_after_sequence,
)


class MiniAppPassengerSynchronizationResumeError(
    ValueError
):
    """
    Raised when passenger synchronization resumption
    cannot be performed safely.
    """


@dataclass(frozen=True)
class MiniAppPassengerSynchronizationResumeResult:
    """
    Deterministic synchronization resume snapshot for
    one authenticated HABESHAGO passenger.
    """

    trip: Trip

    passenger_id: int
    ride_id: int
    driver_id: int

    canonical_state: str

    previous_presentation_status: str
    presentation_status: str

    synchronized: bool

    cursor: PassengerSynchronizationCursor

    replay_from_sequence: int

    pending_updates: tuple[
        SynchronizationUpdate,
        ...,
    ]

    latest_available_sequence: int

    caught_up: bool

    @property
    def pending_update_count(self) -> int:
        """
        Return the number of synchronization updates
        still available after the trusted cursor.
        """

        return len(
            self.pending_updates
        )

    @property
    def last_acknowledged_sequence(self) -> int:
        """
        Return the passenger's trusted synchronization
        acknowledgement position.
        """

        return self.cursor.last_sequence


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
        raise MiniAppPassengerSynchronizationResumeError(
            (
                f"{field_name} must be a "
                "positive integer."
            )
        )

    return value


def resume_passenger_synchronization(
    *,
    trip: Trip,
    passenger_id: int,
) -> MiniAppPassengerSynchronizationResumeResult:
    """
    Build one deterministic passenger synchronization
    resume snapshot.

    The authenticated passenger identity must match the
    canonical passenger already bound to the Mini App Trip.

    Resume performs three coordinated reads:

    1. recover Mini App presentation from authoritative
       canonical Ride state;
    2. read the passenger's trusted synchronization cursor;
    3. replay pending synchronization updates occurring
       strictly after that cursor.

    Resume is non-destructive.

    It never acknowledges updates, never advances the
    synchronization cursor, and never transitions canonical
    Ride state.
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
        raise MiniAppPassengerSynchronizationResumeError(
            "trip must be a Trip."
        )

    try:
        recovery_result = (
            recover_passenger_synchronization(
                trip=trip,
                passenger_id=(
                    authenticated_passenger_id
                ),
            )
        )
    except (
        MiniAppPassengerSynchronizationRecoveryError
    ) as exc:
        raise (
            MiniAppPassengerSynchronizationResumeError(
                str(exc)
            )
        ) from exc

    try:
        cursor = (
            get_passenger_synchronization_cursor(
                authenticated_passenger_id
            )
        )

        pending_updates = tuple(
            get_pending_passenger_updates_after_sequence(
                passenger_id=(
                    authenticated_passenger_id
                ),
                after_sequence=(
                    cursor.last_sequence
                ),
            )
        )
    except ValueError as exc:
        raise (
            MiniAppPassengerSynchronizationResumeError(
                str(exc)
            )
        ) from exc

    if pending_updates:
        latest_available_sequence = max(
            update.sequence
            for update in pending_updates
        )
    else:
        latest_available_sequence = (
            cursor.last_sequence
        )

    return MiniAppPassengerSynchronizationResumeResult(
        trip=trip,
        passenger_id=authenticated_passenger_id,
        ride_id=recovery_result.ride_id,
        driver_id=recovery_result.driver_id,
        canonical_state=(
            recovery_result.canonical_state
        ),
        previous_presentation_status=(
            recovery_result
            .previous_presentation_status
        ),
        presentation_status=(
            recovery_result.presentation_status
        ),
        synchronized=(
            recovery_result.synchronized
        ),
        cursor=cursor,
        replay_from_sequence=(
            cursor.last_sequence
        ),
        pending_updates=pending_updates,
        latest_available_sequence=(
            latest_available_sequence
        ),
        caught_up=(
            len(pending_updates) == 0
        ),
    )