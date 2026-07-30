"""
Passenger Dashboard

Main dashboard for HABESHAGO passengers.
"""

from app.mini_app.components.navigation_item import NavigationItem
from app.mini_app.components.service_card import ServiceCard


def get_dashboard():
    """
    Returns dashboard data.
    """

    navigation = [
        NavigationItem("Home", "/", "🏠").to_dict(),
        NavigationItem("My Rides", "/rides", "🚖").to_dict(),
        NavigationItem("Profile", "/profile", "👤").to_dict(),
    ]

    services = [
        ServiceCard("🚖 Ride", True).to_dict(),
        ServiceCard("🚌 Transit", False).to_dict(),
        ServiceCard("📦 Logistics", False).to_dict(),
    ]

    return {
        "page": "Passenger Dashboard",
        "navigation": navigation,
        "services": services,
    }


if __name__ == "__main__":
    print(get_dashboard())