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

from app.services.synchronization_engine import (
    build_synchronization_update,
)


_PENDING_UPDATES: dict[
    str,
    deque[SynchronizationUpdate],
] = defaultdict(deque)


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