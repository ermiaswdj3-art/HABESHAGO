"""
HABESHAGO Trip Context

Stores the active passenger journey shared across the Mini App.
"""

from app.mini_app.models import Trip


_current_trip = Trip()


def get_trip() -> Trip:
    """
    Return the current active trip.
    """

    return _current_trip


def reset_trip() -> Trip:
    """
    Replace the current trip with a new empty trip.
    """

    global _current_trip

    _current_trip = Trip()

    return _current_trip


def set_destination(
    destination: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> None:
    """
    Store the passenger's selected destination.

    Destination coordinates remain optional for backward
    compatibility while the Mini App transitions from
    demonstration destination data to canonical location
    context.
    """

    _current_trip.destination = destination
    _current_trip.destination_latitude = latitude
    _current_trip.destination_longitude = longitude

def set_pickup(
    latitude: float,
    longitude: float,
    name: str = "Selected on Map",
) -> None:
    """
    Store the passenger's selected pickup location.
    """

    _current_trip.pickup_latitude = latitude
    _current_trip.pickup_longitude = longitude
    _current_trip.pickup_name = name