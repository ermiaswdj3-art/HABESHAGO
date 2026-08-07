"""
HABESHAGO Notification Engine

Converts supported platform events into canonical
Notification intents.

The Notification Engine decides:
- Who should be notified
- What the notification means
- Which delivery channels are appropriate
- Notification priority

It does not perform delivery.
"""

from app.constants.event_types import (
    EventType,
)

from app.constants.notification import (
    NotificationCategory,
    NotificationChannel,
    NotificationPriority,
    NotificationRecipient,
)

from app.models.event import (
    Event,
)

from app.models.notification import (
    Notification,
)


DRIVER_ADMINISTRATION_EVENT_TYPES = {
    EventType.DRIVER_APPROVED,
    EventType.DRIVER_REJECTED,
    EventType.DRIVER_SUSPENDED,
    EventType.DRIVER_RESTORED,
    EventType.DRIVER_RESUBMITTED,
}


def _build_driver_admin_message(
    event: Event,
) -> tuple[str, str, str]:
    """
    Return title, message, and priority for one Driver
    Administration event.
    """

    registration_status = (
        event.payload.get(
            "to_registration_status"
        )
    )

    reason = event.payload.get(
        "reason"
    )

    reason_text = (
        f"\n\nReason:\n{reason}"
        if reason
        else ""
    )

    messages = {
        EventType.DRIVER_APPROVED: (
            "Driver Registration Approved",
            (
                "Your HABESHAGO driver registration "
                "has been approved.\n\n"
                "You may open your Driver Dashboard "
                "and choose when to go online."
            ),
            NotificationPriority.NORMAL,
        ),
        EventType.DRIVER_REJECTED: (
            "Driver Application Rejected",
            (
                "Your HABESHAGO driver application "
                "has been rejected."
            ),
            NotificationPriority.HIGH,
        ),
        EventType.DRIVER_SUSPENDED: (
            "Driver Account Suspended",
            (
                "Your HABESHAGO driver account "
                "has been suspended.\n\n"
                "You have been placed offline and "
                "cannot receive new ride offers."
            ),
            NotificationPriority.CRITICAL,
        ),
        EventType.DRIVER_RESTORED: (
            "Driver Account Restored",
            (
                "Your HABESHAGO driver account "
                "has been restored.\n\n"
                "Your account remains offline until "
                "you voluntarily go online."
            ),
            NotificationPriority.HIGH,
        ),
        EventType.DRIVER_RESUBMITTED: (
            "Driver Verification Restarted",
            (
                "Your HABESHAGO driver application "
                "has been returned to verification.\n\n"
                "Your identity and vehicle records "
                "are waiting for a new review."
            ),
            NotificationPriority.NORMAL,
        ),
    }

    notification_data = messages.get(
        event.event_type
    )

    if notification_data is None:
        raise ValueError(
            "Unsupported Driver Administration "
            "notification event."
        )

    title, message, priority = (
        notification_data
    )

    status_text = (
        "\n\nCurrent Registration Status: "
        f"{registration_status}"
        if registration_status
        else ""
    )

    return (
        title,
        (
            message
            + status_text
            + reason_text
        ),
        priority,
    )


def build_notification(
    event: Event,
) -> Notification | None:
    """
    Convert a supported platform event into a canonical
    Notification intent.

    Return None when the event currently has no
    notification contract.
    """

    if (
        event.event_type
        not in DRIVER_ADMINISTRATION_EVENT_TYPES
    ):
        return None

    driver_id = event.payload.get(
        "driver_id"
    )

    if driver_id is None:
        raise ValueError(
            "Driver Administration notification "
            "is missing driver ID."
        )

    title, message, priority = (
        _build_driver_admin_message(
            event
        )
    )

    return Notification(
        recipient_type=(
            NotificationRecipient.DRIVER
        ),
        recipient_id=int(
            driver_id
        ),
        event_id=event.event_id,
        event_type=event.event_type,
        category=(
            NotificationCategory.DRIVER_ADMINISTRATION
        ),
        title=title,
        message=message,
        priority=priority,
        channels=(
            NotificationChannel.TELEGRAM,
        ),
        metadata={
            "action_reference": (
                event.payload.get(
                    "action_reference"
                )
            ),
            "action_type": (
                event.payload.get(
                    "action_type"
                )
            ),
            "actor_id": (
                event.payload.get(
                    "actor_id"
                )
            ),
        },
    )