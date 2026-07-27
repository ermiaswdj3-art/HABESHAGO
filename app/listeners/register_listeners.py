"""
HABESHAGO Listener Registration

This module connects platform listeners
to the Event Bus.
"""

from app.constants.event_types import (
    EventType,
)

from app.listeners.passenger_notification_listener import (
    passenger_notification_listener,
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

    subscribe(
        EventType.STATE_CHANGED,
        passenger_notification_listener,
    )

    _listeners_registered = True
