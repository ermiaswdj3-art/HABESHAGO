"""
Navigation Item Component

Represents one navigation destination in the
HABESHAGO Telegram Mini App.
"""


class NavigationItem:
    def __init__(
        self,
        label: str,
        route: str,
        icon: str,
        enabled: bool = True,
    ):
        self.label = label
        self.route = route
        self.icon = icon
        self.enabled = enabled

    def to_dict(self):
        """
        Converts the navigation item into a dictionary.
        """

        return {
            "label": self.label,
            "route": self.route,
            "icon": self.icon,
            "enabled": self.enabled,
        }


if __name__ == "__main__":
    home = NavigationItem(
        label="Home",
        route="/",
        icon="🏠",
    )

    rides = NavigationItem(
        label="My Rides",
        route="/rides",
        icon="🚖",
    )

    print(home.to_dict())
    print(rides.to_dict())