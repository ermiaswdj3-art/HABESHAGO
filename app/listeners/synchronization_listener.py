"""
HABESHAGO Synchronization Listener

Consumes platform events and converts them
into synchronization updates for the relevant
platform targets.
"""

import logging

from app.models.event import (
    Event,
)

from app.services.synchronization_service import (
    synchronize_event,
)

logger = logging.getLogger(__name__)


def synchronization_listener(
    event: Event,
) -> None:
    """
    Build and queue synchronization updates
    for one published platform event.
    """

    update = synchronize_event(event)

    logger.info(
        "Synchronization update created: " "event_id=%s update_id=%s targets=%s",
        event.event_id,
        update.update_id,
        update.targets,
    )
