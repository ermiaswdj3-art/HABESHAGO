"""
HABESHAGO Driver Assignment Page

Displays the driver assigned to the passenger's
confirmed booking.
"""

from app.mini_app.context import get_trip
from app.mini_app.pages.app_shell import get_app_shell


def get_driver_assignment_page():
    """
    Build the Driver Assignment page.
    """

    page = get_app_shell("home")

    trip = get_trip()

    page["title"] = "Driver Found"

    page["subtitle"] = (
        "Your HABESHAGO driver is on the way."
    )

    page["trip"] = trip

    return page