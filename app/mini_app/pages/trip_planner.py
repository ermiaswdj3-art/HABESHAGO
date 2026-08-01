"""
HABESHAGO Trip Planner Page

Displays available mobility options after the passenger
selects a destination and pickup location.
"""

from pprint import pprint

from app.mini_app.context import get_trip
from app.mini_app.pages.app_shell import get_app_shell
from app.mini_app.services.decision_service import (
    generate_mobility_options,
)


def get_trip_planner_page():
    """
    Build and return the Trip Planner page data.
    """

    page = get_app_shell("home")

    trip = get_trip()

    page["title"] = "Trip Planner"

    page["subtitle"] = (
        "Choose the best way to reach your destination."
    )

    page["mobility_options"] = generate_mobility_options(
        trip
    )

    page["trip"] = trip

    return page


if __name__ == "__main__":
    pprint(get_trip_planner_page())