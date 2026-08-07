"""
HABESHAGO Listener Registration

This module connects platform listeners
to the Event Bus.
"""

from app.constants.event_types import (
    EventType,
)

from app.listeners.driver_administration_observability_listener import (
    driver_administration_observability_listener,
)

from app.listeners.passenger_notification_listener import (
    passenger_notification_listener,
)

from app.listeners.synchronization_listener import (
    synchronization_listener,
)

from app.services.event_bus import (
    subscribe,
)


_listeners_registered = False


def register_event_listeners() -> None:
    """
    Register HABESHAGO platform listeners.

    Registration runs only once so the same
    listener is not added repeatedly.
    """

    global _listeners_registered

    if _listeners_registered:
        return

    # ==========================================
    # RIDE STATE LISTENERS
    # ==========================================

    subscribe(
        EventType.STATE_CHANGED,
        passenger_notification_listener,
    )

    subscribe(
        EventType.STATE_CHANGED,
        synchronization_listener,
    )

    # ==========================================
    # DRIVER ADMINISTRATION LISTENERS
    # ==========================================

    driver_administration_event_types = (
        EventType.DRIVER_APPROVED,
        EventType.DRIVER_REJECTED,
        EventType.DRIVER_SUSPENDED,
        EventType.DRIVER_RESTORED,
        EventType.DRIVER_RESUBMITTED,
    )

    for event_type in driver_administration_event_types:
        subscribe(
            event_type,
            driver_administration_observability_listener,
        )

    # ==========================================
    # REGISTRATION COMPLETE
    # ==========================================

    _listeners_registered = True