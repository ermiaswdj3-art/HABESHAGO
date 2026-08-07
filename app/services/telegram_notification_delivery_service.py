"""
HABESHAGO Telegram Notification Delivery Service

Delivers canonical HABESHAGO Notification intents through
Telegram.

Responsibilities:
- Validate Telegram channel eligibility
- Send canonical notification content
- Update in-memory delivery status
- Classify expected Telegram delivery failures

This service does not:
- Build notification meaning
- Change business state
- Read or write the HABESHAGO database
"""

import logging

from telegram.error import (
    BadRequest,
    Forbidden,
    NetworkError,
    RetryAfter,
    TimedOut,
)

from app.constants.notification import (
    NotificationChannel,
    NotificationStatus,
)

from app.models.notification import (
    Notification,
)


logger = logging.getLogger(__name__)


def build_telegram_notification_text(
    notification: Notification,
) -> str:
    """
    Build Telegram-ready text from one canonical
    Notification intent.
    """

    title = str(
        notification.title or ""
    ).strip()

    message = str(
        notification.message or ""
    ).strip()

    if title and message:
        return (
            f"{title}\n\n"
            f"{message}"
        )

    if message:
        return message

    if title:
        return title

    raise ValueError(
        "Notification has no deliverable content."
    )


async def deliver_telegram_notification(
    *,
    bot,
    notification: Notification,
) -> bool:
    """
    Deliver one canonical Notification through Telegram.

    Return True on successful delivery.

    Expected Telegram delivery problems return False and
    mark the in-memory notification as FAILED.

    Business state is never rolled back because notification
    delivery occurs after the originating business action.
    """

    if (
        NotificationChannel.TELEGRAM
        not in notification.channels
    ):
        raise ValueError(
            "Notification is not eligible for "
            "Telegram delivery."
        )

    if notification.recipient_id is None:
        raise ValueError(
            "Notification recipient ID is required."
        )

    text = build_telegram_notification_text(
        notification
    )

    try:
        await bot.send_message(
            chat_id=(
                notification.recipient_id
            ),
            text=text,
        )

    except (
        BadRequest,
        Forbidden,
        NetworkError,
        RetryAfter,
        TimedOut,
    ) as error:
        notification.status = (
            NotificationStatus.FAILED
        )

        logger.warning(
            (
                "Telegram notification delivery "
                "failed: notification_id=%s "
                "event_id=%s recipient_id=%s "
                "error=%s"
            ),
            notification.notification_id,
            notification.event_id,
            notification.recipient_id,
            error,
        )

        return False

    notification.status = (
        NotificationStatus.DELIVERED
    )

    logger.info(
        (
            "Telegram notification delivered: "
            "notification_id=%s "
            "event_id=%s recipient_id=%s"
        ),
        notification.notification_id,
        notification.event_id,
        notification.recipient_id,
    )

    return True