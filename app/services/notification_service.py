"""
HABESHAGO Notification Service

Coordinates canonical Notification intents.

Current responsibilities:
- Convert platform events into notifications
- Queue notifications by recipient type
- Allow controlled retrieval and consumption

Future responsibilities:
- Persistent notification outbox
- Delivery adapters
- Retry handling
- Delivery receipts
- Multi-channel routing
- Offline recovery
"""

from collections import (
    defaultdict,
    deque,
)

from app.models.event import (
    Event,
)

from app.models.notification import (
    Notification,
)

from app.services.notification_engine import (
    build_notification,
)


_PENDING_NOTIFICATIONS: dict[
    str,
    deque[Notification],
] = defaultdict(deque)


def queue_event_notification(
    event: Event,
) -> Notification | None:
    """
    Convert one event into a notification and queue it for
    its recipient type.

    Return None when the event has no notification contract.
    """

    notification = build_notification(
        event
    )

    if notification is None:
        return None

    _PENDING_NOTIFICATIONS[
        notification.recipient_type
    ].append(
        notification
    )

    return notification


def get_pending_notifications(
    recipient_type: str,
) -> list[Notification]:
    """
    Return pending notifications for one recipient type
    without removing them.
    """

    return list(
        _PENDING_NOTIFICATIONS.get(
            recipient_type,
            deque(),
        )
    )

def get_pending_notification_by_action_reference(
    *,
    recipient_type: str,
    recipient_id: int | str,
    action_reference: str,
) -> Notification | None:
    """
    Return one pending notification matching a specific
    recipient and Driver Administration action reference.

    The notification remains queued.
    """

    notifications = _PENDING_NOTIFICATIONS.get(
        recipient_type,
        deque(),
    )

    for notification in notifications:
        if (
            notification.recipient_id
            == recipient_id
            and notification.metadata.get(
                "action_reference"
            )
            == action_reference
        ):
            return notification

    return None


def remove_pending_notification(
    notification_id: str,
) -> bool:
    """
    Remove one notification from its queue by ID.

    Return True when the notification was found and
    removed.
    """

    for recipient_type in list(
        _PENDING_NOTIFICATIONS.keys()
    ):
        notifications = (
            _PENDING_NOTIFICATIONS[
                recipient_type
            ]
        )

        for notification in list(
            notifications
        ):
            if (
                notification.notification_id
                != notification_id
            ):
                continue

            notifications.remove(
                notification
            )

            if not notifications:
                _PENDING_NOTIFICATIONS.pop(
                    recipient_type,
                    None,
                )

            return True

    return False

def pop_pending_notifications(
    recipient_type: str,
) -> list[Notification]:
    """
    Return and remove pending notifications for one
    recipient type.
    """

    notifications = list(
        _PENDING_NOTIFICATIONS.get(
            recipient_type,
            deque(),
        )
    )

    _PENDING_NOTIFICATIONS[
        recipient_type
    ].clear()

    return notifications


def clear_pending_notifications() -> None:
    """
    Remove all in-memory notification intents.

    Intended primarily for tests and controlled resets.
    """

    _PENDING_NOTIFICATIONS.clear()