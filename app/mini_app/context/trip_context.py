"""
HABESHAGO Trip Context

Stores the active passenger journey.
"""

from app.mini_app.models import Trip

_current_trip = Trip()


def get_trip() -> Trip:
    return _current_trip


def reset_trip() -> Trip:
    global _current_trip
    _current_trip = Trip()
    return _current_trip


def set_destination(destination: str) -> None:
    _current_trip.destination = destination


def set_pickup(
    latitude: float,
    longitude: float,
    name: str = "Selected on Map",
) -> None:
    _current_trip.pickup_latitude = latitude
    _current_trip.pickup_longitude = longitude
    _current_trip.pickup_name = name


def load_demo_trip() -> Trip:
    """
    Temporary demo data for Commit #64.

    This will later be replaced by
    Home → Map → Planner.
    """

    trip = reset_trip()

    trip.destination = "Bole Airport"

    trip.pickup_name = "Meskel Square"

    trip.pickup_latitude = 8.9806

    trip.pickup_longitude = 38.7578

    return trip