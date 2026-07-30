"""
HABESHAGO Synchronization Engine

The Synchronization Engine determines
which platform components must receive
updates after business events occur.

This engine does not send notifications.

It only plans synchronization.
"""

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


def build_synchronization_update(
    event: Event,
) -> SynchronizationUpdate:
    """
    Convert a platform event into a
    synchronization update.
    """

    targets: tuple[str, ...]

    if event.event_type == EventType.STATE_CHANGED:
        targets = (
            SynchronizationTarget.PASSENGER,
            SynchronizationTarget.DRIVER,
            SynchronizationTarget.OPERATIONS,
        )

    else:
        targets = ()

    return SynchronizationUpdate(
        event_id=event.event_id,
        event_type=event.event_type,
        entity=event.entity,
        entity_id=event.payload.get("entity_id"),
        targets=targets,
        payload=event.payload,
        source="SynchronizationEngine",
    )
