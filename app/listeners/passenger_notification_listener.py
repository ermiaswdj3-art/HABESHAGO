"""
HABESHAGO Passenger Notification Listener

Listens for platform events that affect
passengers.

Future responsibilities:

- Telegram notifications
- Push notifications
- SMS notifications
- Email notifications
"""

from app.models.event import (
    Event,
)


def passenger_notification_listener(
    event: Event,
) -> None:
    """
    React to passenger-related events.

    This first version simply logs that the
    listener received the event.
    """

    print(
        "[Passenger Listener]",
        event.event_type,
        event.payload,
    )
