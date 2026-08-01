"""
HABESHAGO Booking Summary Page

Displays the passenger's completed booking before
confirmation.
"""

from app.mini_app.context import get_trip
from app.mini_app.pages.app_shell import get_app_shell


def get_booking_summary_page():
    """
    Build the Booking Summary page.
    """

    page = get_app_shell("home")

    trip = get_trip()

    page["title"] = "Booking Summary"

    page["subtitle"] = (
        "Review your trip before requesting a driver."
    )

    page["trip"] = trip

    return page