"""
HABESHAGO Trip Lifecycle Service

Controls the ride lifecycle after secure passenger
pickup verification.

This first version simulates trip progress. Future versions
will use real route, GPS, navigation, and driver updates.
"""

from datetime import datetime, timezone

from app.mini_app.models import Trip


def start_trip(
    trip: Trip,
) -> Trip:
    """
    Start a securely verified trip.
    """

    if not trip.is_ready_to_start_trip():
        raise ValueError(
            "The trip is not ready to start."
        )

    trip.trip_started_at = datetime.now(
        timezone.utc
    ).isoformat()

    trip.trip_progress_percent = 0
    trip.destination_reached = False

    trip.set_booking_status("trip_started")
    trip.set_booking_status("trip_in_progress")

    return trip


def advance_trip_progress(
    trip: Trip,
    progress_increment: int = 20,
) -> Trip:
    """
    Advance the simulated trip toward its destination.
    """

    allowed_states = {
        "trip_started",
        "trip_in_progress",
        "arriving_destination",
    }

    if trip.booking_status not in allowed_states:
        raise ValueError(
            "The trip must be active before progress "
            "can be updated."
        )

    if progress_increment <= 0:
        raise ValueError(
            "progress_increment must be greater than zero."
        )

    trip.trip_progress_percent = min(
        100,
        trip.trip_progress_percent
        + progress_increment,
    )

    if trip.trip_progress_percent >= 100:
        trip.trip_progress_percent = 100
        trip.destination_reached = True
        trip.set_booking_status(
            "arriving_destination"
        )
    else:
        trip.set_booking_status(
            "trip_in_progress"
        )

    return trip


def complete_trip(
    trip: Trip,
) -> Trip:
    """
    Complete a trip after reaching the destination.
    """

    if (
        trip.booking_status
        != "arriving_destination"
        or not trip.destination_reached
    ):
        raise ValueError(
            "The trip cannot be completed before "
            "the destination is reached."
        )

    trip.trip_completed_at = datetime.now(
        timezone.utc
    ).isoformat()

    trip.trip_progress_percent = 100
    trip.destination_reached = True

    trip.set_booking_status("trip_completed")

    return trip