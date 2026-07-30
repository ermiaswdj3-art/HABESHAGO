"""
HABESHAGO Ride Transition Service

This service is the single gateway for
changing a ride's lifecycle state.

Responsibilities:
- Validate ride transitions
- Persist ride state
- Synchronize in-memory ride state
- Publish platform state-change events

Future responsibilities:
- Audit logging
- Analytics
- Notifications
"""

from app.constants.event_types import (
    EventType,
)

from app.database.ride_repository import (
    get_ride_status,
    update_ride_status,
)

from app.models.event import (
    Event,
)

from app.services.event_engine import (
    publish_event,
)

from app.services.ride_state_engine import (
    validate_transition,
)

from app.state.active_ride_state import (
    active_rides,
)


def transition_ride(
    *,
    ride_id: int,
    driver_id: int,
    next_state: str,
) -> str:
    """
    Safely transition a ride to a new state.

    Returns:
        The newly applied ride state.

    Raises:
        ValueError:
            If the ride does not exist or the
            requested transition is invalid.
    """

    # ==========================================
    # LOAD CURRENT STATE
    # ==========================================

    current_state = get_ride_status(ride_id)

    if current_state is None:
        raise ValueError("Ride not found.")

    # ==========================================
    # VALIDATE TRANSITION
    # ==========================================

    validate_transition(
        current_state,
        next_state,
    )

    # ==========================================
    # LOAD ACTIVE-RIDE PARTICIPANTS
    # ==========================================

    active_ride = active_rides.get(driver_id)

    passenger_id = None

    if active_ride is not None:
        passenger_id = active_ride.get("passenger_id")

    # ==========================================
    # UPDATE DATABASE
    # ==========================================

    update_ride_status(
        ride_id,
        next_state,
    )

    # ==========================================
    # SYNCHRONIZE MEMORY
    # ==========================================

    if active_ride is not None:
        active_ride["status"] = next_state

    # ==========================================
    # BUILD PLATFORM EVENT
    # ==========================================

    event = Event(
        event_type=EventType.STATE_CHANGED,
        entity="ride",
        source="RideTransitionService",
        payload={
            "entity_id": ride_id,
            "ride_id": ride_id,
            "driver_id": driver_id,
            "passenger_id": passenger_id,
            "from_state": current_state,
            "to_state": next_state,
        },
    )

    # ==========================================
    # PUBLISH PLATFORM EVENT
    # ==========================================

    publish_event(event)

    return next_state
