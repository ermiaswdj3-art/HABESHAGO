"""
Home Page

Main landing page for the HABESHAGO Telegram Mini App.
"""

from app.mini_app.config.settings import MiniAppSettings
from app.mini_app.components.service_card import ServiceCard


def get_home_page():
    """
    Returns the main page information.
    """

    services = [
        ServiceCard("🚖 Ride", True).to_dict(),
        ServiceCard("🚌 Transit", False).to_dict(),
        ServiceCard("📦 Logistics", False).to_dict(),
    ]

    return {
        "title": f"Welcome to {MiniAppSettings.PLATFORM_NAME}",
        "subtitle": "Engineering Ethiopia's AI-Powered Mobility Future",
        "services": services,
    }


if __name__ == "__main__":
    print(get_home_page())