"""
HABESHAGO Interactive Map Page

This page prepares the data needed to render the interactive map.
"""

from app.mini_app.pages.app_shell import get_app_shell


def get_map_page(mode="light"):
    page = get_app_shell(mode)

    page["layout"]["content"] = {
        "title": "Confirm Your Pickup",
        "subtitle": (
            "We will locate you automatically. Move the map only if you need to adjust your pickup."
        ),
        "map": {
            "center": {
                "latitude": 8.9806,
                "longitude": 38.7578,
            },
            "zoom": 13,
        },
    }

    return page


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_map_page())