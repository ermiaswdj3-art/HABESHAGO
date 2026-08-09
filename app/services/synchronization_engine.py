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


DRIVER_ADMINISTRATION_EVENT_TYPES = {
    EventType.DRIVER_APPROVED,
    EventType.DRIVER_REJECTED,
    EventType.DRIVER_SUSPENDED,
    EventType.DRIVER_RESTORED,
    EventType.DRIVER_RESUBMITTED,
}


PRICING_QUOTE_EVENT_TYPES = {
    EventType.PRICING_QUOTE_ISSUED,
    EventType.PRICING_ADJUSTED,
}


PRICING_FINANCIAL_EVENT_TYPES = {
    EventType.FINANCIAL_ALLOCATION_CREATED,
}

PAYMENT_PASSENGER_EVENT_TYPES = {
    EventType.PAYMENT_TRANSACTION_CREATED,
    EventType.PAYMENT_EXECUTION_RECORDED,
    EventType.PAYMENT_VERIFIED,
}


PAYMENT_FINANCIAL_EVENT_TYPES = {
    EventType.PAYMENT_RECONCILED,
    EventType.PAYMENT_FAILED,
}

def _get_synchronization_targets(
    event: Event,
) -> tuple[str, ...]:
    """
    Return the canonical synchronization targets for one
    platform event.
    """

    # ==========================================
    # RIDE STATE EVENTS
    # ==========================================

    if event.event_type == EventType.STATE_CHANGED:
        return (
            SynchronizationTarget.PASSENGER,
            SynchronizationTarget.DRIVER,
            SynchronizationTarget.OPERATIONS,
        )

    # ==========================================
    # PRICING QUOTE / ADJUSTMENT EVENTS
    # ==========================================

    if (
        event.event_type
        in PRICING_QUOTE_EVENT_TYPES
    ):
        return (
            SynchronizationTarget.PASSENGER,
            SynchronizationTarget.OPERATIONS,
            SynchronizationTarget.ANALYTICS,
        )

    # ==========================================
    # PRICING FINANCIAL EVENTS
    # ==========================================

    if (
        event.event_type
        in PRICING_FINANCIAL_EVENT_TYPES
    ):
        return (
            SynchronizationTarget.DRIVER,
            SynchronizationTarget.ADMIN,
            SynchronizationTarget.OPERATIONS,
            SynchronizationTarget.ANALYTICS,
        )

    # ==========================================
    # PAYMENT PASSENGER EVENTS
    # ==========================================

    if (
        event.event_type
        in PAYMENT_PASSENGER_EVENT_TYPES
    ):
        return (
            SynchronizationTarget.PASSENGER,
            SynchronizationTarget.OPERATIONS,
            SynchronizationTarget.ANALYTICS,
        )

    # ==========================================
    # PAYMENT FINANCIAL EVENTS
    # ==========================================

    if (
        event.event_type
        in PAYMENT_FINANCIAL_EVENT_TYPES
    ):
        return (
            SynchronizationTarget.PASSENGER,
            SynchronizationTarget.DRIVER,
            SynchronizationTarget.ADMIN,
            SynchronizationTarget.OPERATIONS,
            SynchronizationTarget.ANALYTICS,
        )

    # ==========================================
    # DRIVER ADMINISTRATION EVENTS
    # ==========================================

    if (
        event.event_type
        in DRIVER_ADMINISTRATION_EVENT_TYPES
    ):
        return (
            SynchronizationTarget.DRIVER,
            SynchronizationTarget.ADMIN,
            SynchronizationTarget.OPERATIONS,
        )

    # ==========================================
    # UNMAPPED EVENTS
    # ==========================================

    return ()


def build_synchronization_update(
    event: Event,
) -> SynchronizationUpdate:
    """
    Convert a platform event into a canonical
    synchronization update.
    """

    targets = (
        _get_synchronization_targets(
            event
        )
    )

    return SynchronizationUpdate(
        event_id=event.event_id,
        event_type=event.event_type,
        entity=event.entity,
        entity_id=event.payload.get(
            "entity_id"
        ),
        targets=targets,
        payload=dict(
            event.payload
        ),
        source="SynchronizationEngine",
    )