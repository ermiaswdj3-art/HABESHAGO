"""
HABESHAGO Driver Administration Event Service

Converts successful canonical Driver Administration
transitions into platform events.

Responsibilities:
- Map administration actions to official Event Types
- Build one shared driver-administration event payload
- Publish events through the HABESHAGO Event Engine

The durable Driver Administration audit record remains
the historical source of truth.

Events are published only after the underlying atomic
administration transaction has completed successfully.
"""

from app.constants.driver_admin_actions import (
    DriverAdminAction,
)

from app.constants.event_types import (
    EventType,
)

from app.models.event import (
    Event,
)

from app.services.event_engine import (
    publish_event,
)


DRIVER_ADMIN_EVENT_TYPES = {
    DriverAdminAction.APPROVE: (
        EventType.DRIVER_APPROVED
    ),
    DriverAdminAction.REJECT: (
        EventType.DRIVER_REJECTED
    ),
    DriverAdminAction.SUSPEND: (
        EventType.DRIVER_SUSPENDED
    ),
    DriverAdminAction.RESTORE: (
        EventType.DRIVER_RESTORED
    ),
    DriverAdminAction.RESUBMIT: (
        EventType.DRIVER_RESUBMITTED
    ),
}


def get_driver_admin_event_type(
    action_type: str,
) -> str:
    """
    Return the official platform Event Type for one
    Driver Administration action.
    """

    normalized_action = str(
        action_type or ""
    ).strip().upper()

    event_type = (
        DRIVER_ADMIN_EVENT_TYPES.get(
            normalized_action
        )
    )

    if event_type is None:
        raise ValueError(
            "Unsupported Driver Administration "
            "event action."
        )

    return event_type


def build_driver_admin_event(
    transition_result: dict,
) -> Event:
    """
    Build one canonical platform event from a successful
    Driver Administration transition result.

    The result must contain the canonical driver state and
    durable audit action returned by the shared Driver
    Administration Service.
    """

    if not isinstance(
        transition_result,
        dict,
    ):
        raise ValueError(
            "Driver Administration transition "
            "result is required."
        )

    driver = transition_result.get(
        "driver"
    )

    action = transition_result.get(
        "action"
    )

    if not isinstance(driver, dict):
        raise ValueError(
            "Driver Administration result is "
            "missing driver state."
        )

    if not isinstance(action, dict):
        raise ValueError(
            "Driver Administration result is "
            "missing audit action."
        )

    action_type = str(
        action.get(
            "action_type",
            "",
        )
    ).strip().upper()

    event_type = (
        get_driver_admin_event_type(
            action_type
        )
    )

    driver_id = action.get(
        "driver_id",
        driver.get("driver_id"),
    )

    if driver_id is None:
        raise ValueError(
            "Driver Administration event is "
            "missing driver ID."
        )

    action_reference = action.get(
        "action_reference"
    )

    if not action_reference:
        raise ValueError(
            "Driver Administration event is "
            "missing action reference."
        )

    return Event(
        event_type=event_type,
        entity="driver",
        source=(
            "DriverAdministrationService"
        ),
        payload={
            "entity_id": int(
                driver_id
            ),
            "driver_id": int(
                driver_id
            ),
            "actor_id": action.get(
                "actor_id"
            ),
            "action_reference": (
                action_reference
            ),
            "action_type": action_type,
            "reason": action.get(
                "reason"
            ),
            "from_registration_status": (
                action.get(
                    "previous_registration_status"
                )
            ),
            "to_registration_status": (
                action.get(
                    "new_registration_status"
                )
            ),
            "from_identity_status": (
                action.get(
                    "previous_identity_status"
                )
            ),
            "to_identity_status": (
                action.get(
                    "new_identity_status"
                )
            ),
            "from_vehicle_status": (
                action.get(
                    "previous_vehicle_status"
                )
            ),
            "to_vehicle_status": (
                action.get(
                    "new_vehicle_status"
                )
            ),
            "from_operational_status": (
                action.get(
                    "previous_operational_status"
                )
            ),
            "to_operational_status": (
                action.get(
                    "new_operational_status"
                )
            ),
            "active_ride_id_at_transition": (
                action.get(
                    "active_ride_id_at_transition"
                )
            ),
            "audit_created_at": (
                action.get(
                    "created_at"
                )
            ),
        },
    )


def publish_driver_admin_event(
    transition_result: dict,
) -> Event:
    """
    Build and publish one successful Driver Administration
    transition event.

    Return the Event object for observability and testing.
    """

    event = build_driver_admin_event(
        transition_result
    )

    publish_event(
        event
    )

    return event