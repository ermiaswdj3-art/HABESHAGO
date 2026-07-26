"""
HABESHAGO Ride State Engine

This engine defines and validates legal ride
lifecycle transitions throughout the platform.
"""

from app.constants.ride_states import (
    RideState,
)


_ALLOWED_TRANSITIONS = {
    RideState.REQUESTED: {
        RideState.SEARCHING_DRIVER,
        RideState.CANCELLED,
        RideState.EXPIRED,
    },

    RideState.SEARCHING_DRIVER: {
        RideState.DRIVER_ASSIGNED,
        RideState.CANCELLED,
        RideState.EXPIRED,
    },

    RideState.DRIVER_ASSIGNED: {
        RideState.DRIVER_ACCEPTED,
        RideState.SEARCHING_DRIVER,
        RideState.CANCELLED,
        RideState.EXPIRED,
    },

    RideState.DRIVER_ACCEPTED: {
        RideState.DRIVER_EN_ROUTE,
        RideState.DRIVER_ARRIVED,
        RideState.CANCELLED,
    },

    RideState.DRIVER_EN_ROUTE: {
        RideState.DRIVER_ARRIVED,
        RideState.CANCELLED,
    },

    RideState.DRIVER_ARRIVED: {
        RideState.PASSENGER_ON_BOARD,
        RideState.TRIP_STARTED,
        RideState.CANCELLED,
    },

    RideState.PASSENGER_ON_BOARD: {
        RideState.TRIP_STARTED,
        RideState.CANCELLED,
    },

    RideState.TRIP_STARTED: {
        RideState.TRIP_COMPLETED,
    },

    RideState.TRIP_COMPLETED: {
        RideState.RATED,
        RideState.ARCHIVED,
    },

    RideState.RATED: {
        RideState.ARCHIVED,
    },

    RideState.CANCELLED: {
        RideState.ARCHIVED,
    },

    RideState.EXPIRED: {
        RideState.ARCHIVED,
    },

    RideState.ARCHIVED: set(),
}


def get_allowed_transitions(
    current_state: str,
) -> set[str]:
    """
    Return all legal next states for the
    supplied current ride state.
    """

    return set(
        _ALLOWED_TRANSITIONS.get(
            current_state,
            set(),
        )
    )


def can_transition(
    current_state: str,
    next_state: str,
) -> bool:
    """
    Return True when the requested ride-state
    transition is legal.
    """

    return next_state in get_allowed_transitions(
        current_state
    )


def validate_transition(
    current_state: str,
    next_state: str,
) -> None:
    """
    Validate a ride-state transition.

    Raise ValueError when the requested
    transition is not allowed.
    """

    if can_transition(
        current_state,
        next_state,
    ):
        return

    raise ValueError(
        "Invalid HABESHAGO ride transition: "
        f"{current_state} -> {next_state}"
    )

# ==========================================
# RIDE STATE CLASSIFICATION
# ==========================================


_ACTIVE_STATES = {
    RideState.DRIVER_ACCEPTED,
    RideState.DRIVER_EN_ROUTE,
    RideState.DRIVER_ARRIVED,
    RideState.PASSENGER_ON_BOARD,
    RideState.TRIP_STARTED,
}


_TERMINAL_STATES = {
    RideState.TRIP_COMPLETED,
    RideState.CANCELLED,
    RideState.EXPIRED,
    RideState.ARCHIVED,
}


def is_active_state(
    ride_state: str,
) -> bool:
    """
    Return True if the ride is currently active.
    """

    return ride_state in _ACTIVE_STATES


def is_terminal_state(
    ride_state: str,
) -> bool:
    """
    Return True if the ride has reached
    a terminal state.
    """

    return ride_state in _TERMINAL_STATES

# ==========================================
# RIDE PHASES
# ==========================================


def get_ride_phase(
    ride_state: str,
) -> str:
    """
    Return the high-level ride phase.
    """

    if ride_state in {
        RideState.REQUESTED,
        RideState.SEARCHING_DRIVER,
        RideState.DRIVER_ASSIGNED,
    }:
        return "REQUEST"

    if ride_state in {
        RideState.DRIVER_ACCEPTED,
        RideState.DRIVER_EN_ROUTE,
        RideState.DRIVER_ARRIVED,
    }:
        return "PICKUP"

    if ride_state in {
        RideState.PASSENGER_ON_BOARD,
        RideState.TRIP_STARTED,
    }:
        return "TRIP"

    if ride_state in {
        RideState.TRIP_COMPLETED,
        RideState.RATED,
    }:
        return "COMPLETED"

    if ride_state in {
        RideState.CANCELLED,
        RideState.EXPIRED,
        RideState.ARCHIVED,
    }:
        return "CLOSED"

    return "UNKNOWN"