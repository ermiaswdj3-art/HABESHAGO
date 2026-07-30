"""
HABESHAGO Ecosystem Home Screen

Defines the main entry screen for the HABESHAGO
Telegram Mini App.
"""

from app.mini_app.components.service_card import ServiceCard
from app.mini_app.pages.app_shell import get_app_shell


def get_home_page(mode="light"):
    """
    Build the HABESHAGO ecosystem home page.
    """

    app_shell = get_app_shell(mode)

    app_shell["layout"]["content"] = {
        "hero": {
            "title": "Move with HABESHAGO",
            "subtitle": (
                "One platform for rides, public transport, "
                "and delivery services."
            ),
        },
        "services_section": {
            "title": "Choose a Service",
            "services": [
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
        },
        "status_message": (
            "Ride is available now. "
            "Transit and Logistics are coming soon."
        ),
    }

    return app_shell


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_home_page())