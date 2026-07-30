"""
Passenger Dashboard

Defines the passenger dashboard for the
HABESHAGO Mini App.
"""

from app.mini_app.components.service_card import ServiceCard
from app.mini_app.pages.app_shell import get_app_shell


def get_passenger_dashboard(mode="light"):
    app = get_app_shell(mode)

    app["layout"]["content"] = {
        "welcome": {
            "title": "Welcome back!",
            "subtitle": "Where would you like to go today?",
        },

        "quick_actions": [
            "🚖 Request Ride",
            "🕒 Ride History",
            "⭐ Favourite Places",
        ],

        "active_services": [
            ServiceCard(
                title="Ride",
                available=True,
            ).to_dict(),

            ServiceCard(
                title="Transit",
                available=False,
            ).to_dict(),

            ServiceCard(
                title="Logistics",
                available=False,
            ).to_dict(),
        ],
    }

    return app


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_passenger_dashboard())