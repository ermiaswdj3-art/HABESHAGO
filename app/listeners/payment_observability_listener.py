"""
HABESHAGO Payment Observability Listener

Consumes canonical Payment Platform events and exposes
them to HABESHAGO operational observability.

Current responsibilities:
- Observe payment transaction events
- Observe payment execution events
- Observe payment verification events
- Observe payment reconciliation events
- Observe payment failure events
- Preserve payment correlation identifiers
- Produce structured operational logs

This listener never:
- executes payments
- verifies provider evidence
- reconciles payments
- modifies payment state
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


PAYMENT_EVENT_TYPES = {
    EventType.PAYMENT_TRANSACTION_CREATED,
    EventType.PAYMENT_EXECUTION_RECORDED,
    EventType.PAYMENT_VERIFIED,
    EventType.PAYMENT_RECONCILED,
    EventType.PAYMENT_FAILED,
}


def payment_observability_listener(
    event: Event,
) -> None:
    """
    Observe one canonical Payment Platform event.

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
        not in PAYMENT_EVENT_TYPES
    ):
        return

    payload = event.payload

    logger.info(
        (
            "Payment event observed: "
            "event_id=%s "
            "event_type=%s "
            "entity=%s "
            "entity_id=%s "
            "transaction_reference=%s "
            "intent_reference=%s "
            "obligation_reference=%s "
            "provider=%s "
            "provider_reference=%s "
            "payment_method=%s "
            "currency=%s "
            "status=%s "
            "execution_status=%s "
            "verification_status=%s "
            "reconciliation_status=%s"
        ),
        event.event_id,
        event.event_type,
        event.entity,
        payload.get(
            "entity_id"
        ),
        payload.get(
            "transaction_reference"
        ),
        payload.get(
            "intent_reference"
        ),
        payload.get(
            "obligation_reference"
        ),
        payload.get(
            "provider"
        ),
        payload.get(
            "provider_reference"
        ),
        payload.get(
            "payment_method"
        ),
        payload.get(
            "currency"
        ),
        payload.get(
            "status"
        ),
        payload.get(
            "execution_status"
        ),
        payload.get(
            "verification_status"
        ),
        payload.get(
            "reconciliation_status"
        ),
    )