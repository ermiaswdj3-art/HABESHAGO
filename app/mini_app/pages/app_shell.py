"""
Application Shell

Defines the high-level layout of the HABESHAGO Mini App.
"""

from app.mini_app.static.styles import UIStyles


def get_app_shell(mode="light"):
    return {
        "application": "HABESHAGO",
        "layout": {
            "header": {
                "title": "HABESHAGO",
                "subtitle": "Ride • Transit • Logistics",
            },
            "content": {},
            "bottom_navigation": [
                "Home",
                "My Trips",
                "Profile",
            ],
        },
        "styles": {
            "page": UIStyles.page(mode),
            "card": UIStyles.card(mode),
            "button": UIStyles.button(mode),
        },
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_app_shell())