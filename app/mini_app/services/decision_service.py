"""
HABESHAGO Decision Service

Generates mobility options for an active trip.

The first version uses controlled demo estimates.
Future versions can use routing, traffic, driver availability,
transit schedules, weather, and AI recommendations.
"""

from app.mini_app.models import Trip


def generate_mobility_options(trip: Trip) -> list[dict]:
    """
    Generate available mobility options for a trip.

    Args:
        trip:
            The active HABESHAGO trip.

    Returns:
        A list of mobility option dictionaries.
    """

    if not trip.is_ready_for_planning():
        return []

    return [
        {
            "id": "ride",
            "title": "Ride",
            "icon": "\U0001F696",
            "description": "Fast private transportation.",
            "eta": "12 min",
            "price": "210 ETB",
            "badge": "\u2B50 Recommended",
            "recommendation_reason": "Fastest option for this trip.",
            "is_recommended": True,
        },
        {
            "id": "transit",
            "title": "Transit",
            "icon": "\U0001F68C",
            "description": "Affordable public transport.",
            "eta": "32 min",
            "price": "35 ETB",
            "badge": "\U0001F4B0 Cheapest",
            "recommendation_reason": "Save 175 ETB compared with Ride.",
            "is_recommended": False,
        },
        {
            "id": "walk_transit",
            "title": "Walk + Transit",
            "icon": "\U0001F6B6",
            "description": (
                "Walk to the nearest stop, then continue by bus."
            ),
            "eta": "28 min",
            "price": "25 ETB",
            "badge": "\U0001F331 Lowest Emissions",
            "recommendation_reason": (
                "Lowest-cost and lowest-emission option."
            ),
            "is_recommended": False,
        },
    ]