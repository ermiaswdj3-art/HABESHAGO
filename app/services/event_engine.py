"""
HABESHAGO Event Engine

The Event Engine publishes platform events
and delivers them to registered listeners.

Future responsibilities:
- Asynchronous listeners
- Persistent event storage
- Retry handling
- Dead-letter processing
- Distributed event delivery
"""

import logging

from app.models.event import (
    Event,
)

from app.services.event_bus import (
    get_listeners,
)

logger = logging.getLogger(__name__)


def publish_event(
    event: Event,
) -> None:
    """
    Publish a platform event and deliver it
    to every registered listener.

    One listener failure must not prevent
    the remaining listeners from receiving
    the event.
    """

    logger.info(
        "Platform event published: " "type=%s entity=%s source=%s id=%s",
        event.event_type,
        event.entity,
        event.source,
        event.event_id,
    )

    listeners = get_listeners(event.event_type)

    for listener in listeners:
        try:
            listener(event)

        except Exception:
            logger.exception(
                "Event listener failed: " "event_type=%s listener=%s",
                event.event_type,
                getattr(
                    listener,
                    "__name__",
                    repr(listener),
                ),
            )
