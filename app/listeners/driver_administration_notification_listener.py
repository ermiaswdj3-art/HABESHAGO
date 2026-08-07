"""
HABESHAGO Driver Administration Notification Listener

Consumes canonical Driver Administration events and
creates shared Notification intents.

The listener performs no Telegram, SMS, push, or email
delivery.
"""

import logging

from app.models.event import (
    Event,
)

from app.services.notification_service import (
    queue_event_notification,
)


logger = logging.getLogger(__name__)


def driver_administration_notification_listener(
    event: Event,
) -> None:
    """
    Create and queue the notification intent associated
    with one successful Driver Administration event.
    """

    notification = (
        queue_event_notification(
            event
        )
    )

    if notification is None:
        return

    logger.info(
        (
            "Driver Administration notification queued: "
            "event_id=%s "
            "notification_id=%s "
            "recipient_type=%s "
            "recipient_id=%s "
            "channels=%s"
        ),
        event.event_id,
        notification.notification_id,
        notification.recipient_type,
        notification.recipient_id,
        notification.channels,
    )