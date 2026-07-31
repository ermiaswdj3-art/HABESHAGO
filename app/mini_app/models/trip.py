"""
HABESHAGO Trip Model

This module defines the canonical Trip object shared across
the entire HABESHAGO mobility platform.

Every service (Ride, Transit, Logistics, AI, Wallet, Rewards)
will work with this same model.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Trip:

    # Destination chosen by the passenger
    destination: Optional[str] = None

    # Pickup location name
    pickup_name: Optional[str] = None

    # GPS coordinates
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None

    # Passenger information
    passengers: int = 1

    # Selected service
    service: Optional[str] = None

    # Ride category
    category: Optional[str] = None

    # Planner estimates
    estimated_fare: Optional[float] = None
    estimated_eta: Optional[str] = None

    # AI recommendation
    recommendation: Optional[str] = None

    def is_ready_for_planning(self) -> bool:
        """
        Returns True when enough information exists
        to generate mobility options.
        """

        return (
            self.destination is not None
            and self.pickup_latitude is not None
            and self.pickup_longitude is not None
        )