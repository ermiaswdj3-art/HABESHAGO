"""
Driver Dashboard

Defines the driver dashboard for the
HABESHAGO Mini App.
"""

from app.mini_app.pages.app_shell import get_app_shell


def get_driver_dashboard(mode="light"):
    app = get_app_shell(mode)

    app["layout"]["content"] = {
        "welcome": {
            "title": "Driver Dashboard",
            "subtitle": "Manage your availability and ride activity.",
        },
        "availability": {
            "status": "offline",
            "label": "You are currently offline",
            "action": "Go Online",
        },
        "summary": {
            "today_trips": 0,
            "today_earnings": "0.00 ETB",
            "rating": "Not available",
        },
        "quick_actions": [
            "🚘 View Ride Requests",
            "📍 Update Location",
            "💰 Earnings",
            "📜 Trip History",
        ],
    }

    return app


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_driver_dashboard())