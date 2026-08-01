"""
HABESHAGO Driver Model

Defines the canonical Driver object shared across the
HABESHAGO mobility platform.

The Dispatch Engine, Driver App, Tracking Engine,
Navigation, and Fleet Management all use this model.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Driver:
    """
    Represents a HABESHAGO driver.
    """

    # Unique identifier
    driver_id: str

    # Driver information
    name: str

    rating: float

    # Vehicle information
    vehicle: str

    plate_number: str

    vehicle_color: str

    # Current GPS location
    latitude: float

    longitude: float

    # Driver status
    is_online: bool = True

    is_available: bool = True

    # Estimated arrival to passenger
    eta_minutes: Optional[int] = None

    def can_accept_dispatch(self) -> bool:
        """
        Returns True if the driver is able to
        receive a new trip.
        """

        return (
            self.is_online
            and self.is_available
        )