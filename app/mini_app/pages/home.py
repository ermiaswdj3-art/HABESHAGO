"""
HABESHAGO Intelligent Home Page

Builds the destination-first Home experience for the Mini App.
"""

from app.mini_app.pages.app_shell import get_app_shell
from app.mini_app.services.destination_service import (
    get_destination_suggestions,
)


def get_home_page(mode="light"):
    page = get_app_shell(mode)

    page["layout"]["content"] = {
        "greeting": "Welcome to HABESHAGO 👋",
        "headline": "Where are you going today?",
        "search_placeholder": "Search destination...",

        "destination_suggestions": get_destination_suggestions(),

        "recent_places": [
            {
                "icon": "🏠",
                "name": "Home",
                "description": "Your saved home location",
                "destination": "Home",
            },
            {
                "icon": "🏢",
                "name": "Office",
                "description": "Your saved workplace",
                "destination": "Office",
            },
            {
                "icon": "✈️",
                "name": "Airport",
                "description": "Bole International Airport",
                "destination": "Bole International Airport",
            },
            {
                "icon": "⭐",
                "name": "Saved Places",
                "description": "View all favorite destinations",
                "destination": "Saved Places",
            },
        ],

        "platform_status": [
            {
                "icon": "🟢",
                "title": "Ride Available",
            },
            {
                "icon": "🟢",
                "title": "Transit Active",
            },
            {
                "icon": "🟢",
                "title": "Delivery Available",
            },
        ],

        "insights": [
            {
                "icon": "🌧️",
                "title": "Rain expected today",
                "subtitle": "Demand may increase this afternoon.",
            },
            {
                "icon": "🎉",
                "title": "5% Ride Cashback",
                "subtitle": "Available today.",
            },
            {
                "icon": "🏆",
                "title": "Rewards",
                "subtitle": (
                    "Ride three times this week to earn bonus points."
                ),
            },
        ],
    }

    return page


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_home_page())