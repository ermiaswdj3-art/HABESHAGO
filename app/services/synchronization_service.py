"""
HABESHAGO Synchronization Service

Coordinates synchronization updates across
platform targets.

Current responsibilities:
- Convert platform events into synchronization updates
- Build target-aware delivery payloads
- Queue updates for each synchronization target
- Allow platform clients to retrieve pending updates

Future responsibilities:
- Real-time WebSocket delivery
- Telegram delivery coordination
- Retry handling
- Persistent synchronization queues
- Offline-client recovery
"""

from collections import (
    defaultdict,
    deque,
)

from app.constants.event_types import (
    EventType,
)

from app.constants.synchronization_targets import (
    SynchronizationTarget,
)

from app.models.event import (
    Event,
)

from app.models.synchronization_update import (
    SynchronizationUpdate,
)

from app.models.passenger_synchronization_cursor import (
    PassengerSynchronizationCursor,
)

from app.services.synchronization_engine import (
    build_synchronization_update,
)


_PENDING_UPDATES: dict[
    str,
    deque[SynchronizationUpdate],
] = defaultdict(deque)

_SYNCHRONIZATION_SEQUENCE = 0

_PASSENGER_SYNCHRONIZATION_CURSORS: dict[
    int,
    PassengerSynchronizationCursor,
] = {}

def _next_synchronization_sequence() -> int:
    """
    Return the next process-local synchronization
    delivery sequence.

    Sequence values are strictly increasing within
    the running synchronization service process.
    """

    global _SYNCHRONIZATION_SEQUENCE

    _SYNCHRONIZATION_SEQUENCE += 1

    return _SYNCHRONIZATION_SEQUENCE

PAYMENT_EVENT_TYPES = {
    EventType.PAYMENT_TRANSACTION_CREATED,
    EventType.PAYMENT_EXECUTION_RECORDED,
    EventType.PAYMENT_VERIFIED,
    EventType.PAYMENT_RECONCILED,
    EventType.PAYMENT_FAILED,
}


PASSENGER_PAYMENT_ALLOWED_FIELDS = {
    "entity_id",
    "transaction_reference",
    "obligation_reference",
    "provider",
    "payment_method",
    "currency",
    "amount",
    "status",
    "execution_status",
    "verification_status",
    "reconciliation_status",
    "created_at",
    "processed_at",
    "verified_at",
    "reconciled_at",
}


DRIVER_PAYMENT_ALLOWED_FIELDS = {
    "entity_id",
    "transaction_reference",
    "provider",
    "currency",
    "amount",
    "reconciliation_status",
}


def _filter_payload(
    payload: dict,
    *,
    allowed_fields: set[str],
) -> dict:
    """
    Return only explicitly permitted synchronization
    payload fields.
    """

    return {
        key: value
        for key, value in payload.items()
        if key in allowed_fields
    }


def _build_target_payload(
    *,
    event: Event,
    target: str,
) -> dict:
    """
    Build the payload permitted for one synchronization
    target.

    Canonical platform events remain unchanged.

    Only the queued client-facing synchronization payload
    is filtered.
    """

    payload = dict(
        event.payload
    )

    if (
        event.event_type
        not in PAYMENT_EVENT_TYPES
    ):
        return payload

    # ==========================================
    # PASSENGER PAYMENT PAYLOAD
    # ==========================================

    if (
        target
        == SynchronizationTarget.PASSENGER
    ):
        return _filter_payload(
            payload,
            allowed_fields=(
                PASSENGER_PAYMENT_ALLOWED_FIELDS
            ),
        )

    # ==========================================
    # DRIVER PAYMENT PAYLOAD
    # ==========================================

    if (
        target
        == SynchronizationTarget.DRIVER
    ):
        return _filter_payload(
            payload,
            allowed_fields=(
                DRIVER_PAYMENT_ALLOWED_FIELDS
            ),
        )

    # ==========================================
    # ADMINISTRATION / OPERATIONS / ANALYTICS
    # ==========================================

    if target in {
        SynchronizationTarget.ADMIN,
        SynchronizationTarget.OPERATIONS,
        SynchronizationTarget.ANALYTICS,
    }:
        return payload

    # ==========================================
    # OTHER TARGETS
    # ==========================================

    return payload


def synchronize_event(
    event: Event,
) -> SynchronizationUpdate:
    """
    Convert an event into a synchronization plan and queue
    one target-specific update for every target.

    The returned update represents the full synchronization
    plan.

    Queued updates may carry target-specific payloads so
    sensitive platform data is not unnecessarily exposed
    to client-facing targets.
    """

    update = build_synchronization_update(
        event
    )

    for target in update.targets:
        target_update = SynchronizationUpdate(
            event_id=update.event_id,
            event_type=update.event_type,
            entity=update.entity,
            entity_id=update.entity_id,
            targets=(
                target,
            ),
            payload=_build_target_payload(
                event=event,
                target=target,
            ),
            source=update.source,
            version=update.version,
            sequence=_next_synchronization_sequence(),
        )

        _PENDING_UPDATES[
            target
        ].append(
            target_update
        )

    return update


def get_pending_updates(
    target: str,
) -> list[SynchronizationUpdate]:
    """
    Return the pending synchronization updates
    for one target without removing them.
    """

    return list(
        _PENDING_UPDATES.get(
            target,
            deque(),
        )
    )


def pop_pending_updates(
    target: str,
) -> list[SynchronizationUpdate]:
    """
    Return and remove all pending updates for
    one synchronization target.
    """

    updates = list(
        _PENDING_UPDATES.get(
            target,
            deque(),
        )
    )

    _PENDING_UPDATES[
        target
    ].clear()

    return updates


def clear_pending_updates() -> None:
    """
    Remove every queued synchronization update.

    Intended primarily for testing and controlled
    application resets.
    """

    _PENDING_UPDATES.clear()

def get_passenger_synchronization_cursor(
    passenger_id: int,
) -> PassengerSynchronizationCursor:
    """
    Return the synchronization cursor belonging to one
    canonical HABESHAGO passenger.

    A passenger without recorded progress begins at
    synchronization sequence zero.
    """

    if (
        not isinstance(passenger_id, int)
        or isinstance(passenger_id, bool)
        or passenger_id <= 0
    ):
        raise ValueError(
            "passenger_id must be a positive integer."
        )

    cursor = _PASSENGER_SYNCHRONIZATION_CURSORS.get(
        passenger_id
    )

    if cursor is None:
        cursor = PassengerSynchronizationCursor(
            passenger_id=passenger_id,
            last_sequence=0,
        )

        _PASSENGER_SYNCHRONIZATION_CURSORS[
            passenger_id
        ] = cursor

    return cursor


def advance_passenger_synchronization_cursor(
    *,
    passenger_id: int,
    sequence: int,
) -> PassengerSynchronizationCursor:
    """
    Advance one canonical passenger's synchronization
    cursor to a processed sequence.

    Cursor movement is monotonic.

    Repeating the current sequence is idempotent.

    The cursor may never move backward.
    """

    if (
        not isinstance(passenger_id, int)
        or isinstance(passenger_id, bool)
        or passenger_id <= 0
    ):
        raise ValueError(
            "passenger_id must be a positive integer."
        )

    if (
        not isinstance(sequence, int)
        or isinstance(sequence, bool)
        or sequence < 0
    ):
        raise ValueError(
            "sequence must be a non-negative integer."
        )

    current_cursor = (
        get_passenger_synchronization_cursor(
            passenger_id
        )
    )

    if sequence < current_cursor.last_sequence:
        raise ValueError(
            (
                "Passenger synchronization cursor "
                "cannot move backward."
            )
        )

    if sequence == current_cursor.last_sequence:
        return current_cursor

    cursor = PassengerSynchronizationCursor(
        passenger_id=passenger_id,
        last_sequence=sequence,
    )

    _PASSENGER_SYNCHRONIZATION_CURSORS[
        passenger_id
    ] = cursor

    return cursor

def get_pending_passenger_updates(
    passenger_id: int,
) -> list[SynchronizationUpdate]:
    """
    Return pending passenger synchronization updates
    belonging to one canonical HABESHAGO passenger.

    The shared passenger queue remains unchanged.

    This helper only exposes updates whose canonical
    event payload identifies the requested passenger.
    """

    if (
        not isinstance(passenger_id, int)
        or isinstance(passenger_id, bool)
        or passenger_id <= 0
    ):
        raise ValueError(
            "passenger_id must be a positive integer."
        )

    passenger_updates = get_pending_updates(
        SynchronizationTarget.PASSENGER
    )

    return [
        update
        for update in passenger_updates
        if update.payload.get("passenger_id")
        == passenger_id
    ]

def get_pending_passenger_updates_after_sequence(
    *,
    passenger_id: int,
    after_sequence: int,
) -> list[SynchronizationUpdate]:
    """
    Return pending passenger synchronization updates
    occurring strictly after one synchronization sequence.

    The read is non-destructive.

    Only updates belonging to the requested canonical
    passenger are returned.

    after_sequence=0 returns every currently pending
    update belonging to that passenger.
    """

    if (
        not isinstance(passenger_id, int)
        or isinstance(passenger_id, bool)
        or passenger_id <= 0
    ):
        raise ValueError(
            "passenger_id must be a positive integer."
        )

    if (
        not isinstance(after_sequence, int)
        or isinstance(after_sequence, bool)
        or after_sequence < 0
    ):
        raise ValueError(
            (
                "after_sequence must be a "
                "non-negative integer."
            )
        )

    passenger_updates = (
        get_pending_passenger_updates(
            passenger_id
        )
    )

    return [
        update
        for update in passenger_updates
        if update.sequence > after_sequence
    ]

def pop_pending_passenger_updates(
    passenger_id: int,
) -> list[SynchronizationUpdate]:
    """
    Return and remove pending passenger synchronization
    updates belonging to one canonical passenger.

    Updates belonging to other passengers remain queued.
    """

    if (
        not isinstance(passenger_id, int)
        or isinstance(passenger_id, bool)
        or passenger_id <= 0
    ):
        raise ValueError(
            "passenger_id must be a positive integer."
        )

    passenger_queue = _PENDING_UPDATES[
        SynchronizationTarget.PASSENGER
    ]

    matched_updates = []
    retained_updates = deque()

    while passenger_queue:
        update = passenger_queue.popleft()

        if (
            update.payload.get("passenger_id")
            == passenger_id
        ):
            matched_updates.append(update)
        else:
            retained_updates.append(update)

    passenger_queue.extend(
        retained_updates
    )

    return matched_updates

def acknowledge_pending_passenger_update(
    *,
    passenger_id: int,
    update_id: str,
) -> SynchronizationUpdate | None:
    """
    Acknowledge and remove one pending synchronization
    update belonging to one canonical passenger.

    Only the exact update identified by update_id is
    removed.

    Updates belonging to other passengers and other
    updates belonging to the same passenger remain queued.
    """

    if (
        not isinstance(passenger_id, int)
        or isinstance(passenger_id, bool)
        or passenger_id <= 0
    ):
        raise ValueError(
            "passenger_id must be a positive integer."
        )

    if (
        not isinstance(update_id, str)
        or not update_id.strip()
    ):
        raise ValueError(
            "update_id must be a non-empty string."
        )

    clean_update_id = update_id.strip()

    passenger_queue = _PENDING_UPDATES[
        SynchronizationTarget.PASSENGER
    ]

    acknowledged_update = None
    retained_updates = deque()

    while passenger_queue:
        update = passenger_queue.popleft()

        belongs_to_passenger = (
            update.payload.get("passenger_id")
            == passenger_id
        )

        matches_update = (
            update.update_id
            == clean_update_id
        )

        if (
            acknowledged_update is None
            and belongs_to_passenger
            and matches_update
        ):
            acknowledged_update = update
            continue

        retained_updates.append(
            update
        )

    passenger_queue.extend(
        retained_updates
    )

    return acknowledged_update

def acknowledge_pending_passenger_update_in_order(
    *,
    passenger_id: int,
    update_id: str,
) -> tuple[
    SynchronizationUpdate,
    PassengerSynchronizationCursor,
] | None:
    """
    Acknowledge the next eligible synchronization update
    belonging to one canonical passenger and advance that
    passenger's trusted synchronization cursor.

    Acknowledgement is ordered.

    A passenger may acknowledge only the earliest pending
    synchronization update belonging to that passenger.

    All validation occurs before queue or cursor mutation.
    """

    if (
        not isinstance(passenger_id, int)
        or isinstance(passenger_id, bool)
        or passenger_id <= 0
    ):
        raise ValueError(
            "passenger_id must be a positive integer."
        )

    if (
        not isinstance(update_id, str)
        or not update_id.strip()
    ):
        raise ValueError(
            "update_id must be a non-empty string."
        )

    clean_update_id = update_id.strip()

    passenger_queue = _PENDING_UPDATES[
        SynchronizationTarget.PASSENGER
    ]

    earliest_passenger_update = None
    matching_update = None

    for update in passenger_queue:
        if (
            update.payload.get("passenger_id")
            != passenger_id
        ):
            continue

        if earliest_passenger_update is None:
            earliest_passenger_update = update

        if update.update_id == clean_update_id:
            matching_update = update

    if matching_update is None:
        return None

    if (
        earliest_passenger_update is None
        or earliest_passenger_update.update_id
        != matching_update.update_id
    ):
        raise ValueError(
            (
                "Passenger synchronization updates "
                "must be acknowledged in order."
            )
        )

    current_cursor = (
        get_passenger_synchronization_cursor(
            passenger_id
        )
    )

    if (
        matching_update.sequence
        < current_cursor.last_sequence
    ):
        raise ValueError(
            (
                "Passenger synchronization cursor "
                "cannot move backward."
            )
        )

    if (
        matching_update.sequence
        == current_cursor.last_sequence
    ):
        next_cursor = current_cursor
    else:
        next_cursor = PassengerSynchronizationCursor(
            passenger_id=passenger_id,
            last_sequence=matching_update.sequence,
        )

    retained_updates = deque()
    removed = False

    for update in passenger_queue:
        if (
            not removed
            and update is matching_update
        ):
            removed = True
            continue

        retained_updates.append(
            update
        )

    passenger_queue.clear()
    passenger_queue.extend(
        retained_updates
    )

    _PASSENGER_SYNCHRONIZATION_CURSORS[
        passenger_id
    ] = next_cursor

    return (
        matching_update,
        next_cursor,
    )