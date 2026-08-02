"""
HABESHAGO Active Trip Page

Displays the passenger's active ride after secure
pickup verification and trip start.
"""

from app.mini_app.context import get_trip
from app.mini_app.pages.app_shell import get_app_shell


def get_active_trip_page():
    """
    Build the Active Trip page.
    """

    page = get_app_shell("home")

    trip = get_trip()

    page["title"] = "Trip in Progress"

    page["subtitle"] = (
        "Follow your HABESHAGO journey to the destination."
    )

    page["trip"] = trip

    return page