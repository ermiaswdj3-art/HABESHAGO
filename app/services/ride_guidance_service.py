from app.constants.ride_states import (
    RideState,
)

"""
HABESHAGO Ride Guidance Engine

This service is responsible for determining
what guidance should be presented to a driver
based on the current ride state.

Future responsibilities:
- Next action
- Driver mission
- Navigation guidance
- ETA guidance
- Safety reminders
"""


GUIDANCE = {
    RideState.DRIVER_ACCEPTED: {
        "status": "✅ Driver Accepted",
        "next_action": "📍 Drive to the pickup location.",
        "mission": "Pick up your passenger.",
    },
    RideState.DRIVER_ARRIVED: {
        "status": "📍 Waiting at Pickup",
        "next_action": "👤 Wait for the passenger to board.",
        "mission": "Prepare to begin the trip.",
    },
    RideState.TRIP_STARTED: {
        "status": "🚕 Trip in Progress",
        "next_action": "🏁 Drive safely to the destination.",
        "mission": "Complete the ride safely.",
    },
}


def get_ride_guidance(
    ride_status: str | None,
):
    """
    Return guidance for the current ride state.

    If no active ride exists, return the
    driver's idle guidance.
    """

    if ride_status is None:
        return {
            "status": "✅ Waiting for Ride",
            "next_action": (
                "🟢 Stay online to receive ride requests."
            ),
            "mission": (
                "Ready to accept your next passenger."
            ),
        }

    return GUIDANCE.get(
        ride_status,
        {
            "status": ride_status,
            "next_action": (
                "🚖 Continue your current ride."
            ),
            "mission": (
                "Complete the current workflow."
            ),
        },
    )