"""
Service Card Component

Reusable card representing one HABESHAGO service.
"""


class ServiceCard:
    def __init__(self, title, available):
        self.title = title
        self.available = available

    def to_dict(self):
        return {
            "title": self.title,
            "available": self.available,
        }


if __name__ == "__main__":
    ride = ServiceCard("🚖 Ride", True)

    transit = ServiceCard("🚌 Transit", False)

    print(ride.to_dict())

    print(transit.to_dict())