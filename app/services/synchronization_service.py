"""
HABESHAGO Synchronization Service

Coordinates synchronization updates across
platform targets.

Current responsibilities:
- Convert platform events into synchronization updates
- Queue updates for each synchronization target
- Allow platform clients to retrieve pending updates

Future responsibilities:
- Real-time WebSocket delivery
- Telegram delivery coordination
- Retry handling
- Persistent synchronization queues
- Offline-client recovery
"""

from collections import defaultdict
from collections import deque

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


def synchronize_event(
    event: Event,
) -> SynchronizationUpdate:
    """
    Convert an event into a synchronization
    update and queue it for every target.
    """

    update = build_synchronization_update(event)

    for target in update.targets:
        _PENDING_UPDATES[target].append(update)

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

    _PENDING_UPDATES[target].clear()

    return updates


def clear_pending_updates() -> None:
    """
    Remove every queued synchronization update.

    Intended primarily for testing and controlled
    application resets.
    """

    _PENDING_UPDATES.clear()
