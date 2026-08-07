"""
HABESHAGO Notification Model

Represents one canonical notification intent prepared by
the shared Notification Platform.

A Notification describes what should be communicated.

Delivery channels such as Telegram, push, SMS, or email
remain separate concerns.
"""

from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from typing import Any

import uuid

from app.constants.notification import (
    NotificationPriority,
    NotificationStatus,
)


@dataclass(slots=True)
class Notification:
    """
    Canonical HABESHAGO notification intent.
    """

    notification_id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    recipient_type: str = ""

    recipient_id: int | str | None = None

    event_id: str = ""

    event_type: str = ""

    category: str = ""

    title: str = ""

    message: str = ""

    priority: str = (
        NotificationPriority.NORMAL
    )

    channels: tuple[str, ...] = field(
        default_factory=tuple
    )

    status: str = (
        NotificationStatus.PENDING
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=lambda: (
            datetime.now(
                timezone.utc
            )
        )
    )