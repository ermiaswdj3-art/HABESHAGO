"""
HABESHAGO Driver Administration Observability Listener

Consumes canonical Driver Administration platform events
and exposes them to HABESHAGO operational observability.

Current responsibilities:
- Validate the basic administration-event contract
- Produce structured operational logs
- Preserve action-reference correlation

Future responsibilities:
- Admin monitoring dashboards
- Security alerts
- Compliance reporting
- Analytics pipelines
- Distributed observability
"""

import logging

from app.models.event import (
    Event,
)


logger = logging.getLogger(__name__)


def driver_administration_observability_listener(
    event: Event,
) -> None:
    """
    Observe one successful Driver Administration event.

    This listener never changes driver state.
    """

    payload = event.payload

    driver_id = payload.get(
        "driver_id"
    )

    actor_id = payload.get(
        "actor_id"
    )

    action_type = payload.get(
        "action_type"
    )

    action_reference = payload.get(
        "action_reference"
    )

    from_registration_status = payload.get(
        "from_registration_status"
    )

    to_registration_status = payload.get(
        "to_registration_status"
    )

    from_operational_status = payload.get(
        "from_operational_status"
    )

    to_operational_status = payload.get(
        "to_operational_status"
    )

    logger.info(
        (
            "Driver Administration event observed: "
            "event_id=%s "
            "event_type=%s "
            "driver_id=%s "
            "actor_id=%s "
            "action=%s "
            "action_reference=%s "
            "registration=%s->%s "
            "operations=%s->%s"
        ),
        event.event_id,
        event.event_type,
        driver_id,
        actor_id,
        action_type,
        action_reference,
        from_registration_status,
        to_registration_status,
        from_operational_status,
        to_operational_status,
    )