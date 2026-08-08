"""
HABESHAGO Pricing Observability Listener

Consumes canonical Pricing Platform events and exposes
them to HABESHAGO operational observability.

Current responsibilities:
- Observe pricing quote events
- Observe governed pricing adjustment events
- Observe financial allocation events
- Preserve pricing and financial correlation identifiers
- Produce structured operational logs

This listener never:
- recalculates fares
- applies adjustments
- calculates commission
- modifies pricing state
- modifies settlement state
"""

import logging

from app.constants.event_types import (
    EventType,
)

from app.models.event import (
    Event,
)


logger = logging.getLogger(__name__)


PRICING_EVENT_TYPES = {
    EventType.PRICING_QUOTE_ISSUED,
    EventType.PRICING_ADJUSTED,
    EventType.FINANCIAL_ALLOCATION_CREATED,
}


def pricing_observability_listener(
    event: Event,
) -> None:
    """
    Observe one canonical Pricing Platform event.

    The listener is strictly read-only.
    """

    if not isinstance(
        event,
        Event,
    ):
        raise ValueError(
            "event must be an Event."
        )

    if (
        event.event_type
        not in PRICING_EVENT_TYPES
    ):
        return

    payload = event.payload

    logger.info(
        (
            "Pricing event observed: "
            "event_id=%s "
            "event_type=%s "
            "entity=%s "
            "entity_id=%s "
            "quote_id=%s "
            "request_id=%s "
            "ride_id=%s "
            "pricing_version=%s "
            "configuration_version=%s "
            "adjustment_references=%s "
            "commission_policy_version=%s"
        ),
        event.event_id,
        event.event_type,
        event.entity,
        payload.get(
            "entity_id"
        ),
        payload.get(
            "quote_id"
        ),
        payload.get(
            "request_id"
        ),
        payload.get(
            "ride_id"
        ),
        payload.get(
            "pricing_version"
        ),
        payload.get(
            "configuration_version"
        ),
        payload.get(
            "adjustment_references"
        ),
        payload.get(
            "commission_policy_version"
        ),
    )