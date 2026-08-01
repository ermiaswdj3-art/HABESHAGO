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

    # Selected route (future routing engine)
    selected_route: Optional[str] = None

    # Booking lifecycle
    booking_status: str = "planning"

    # Booking creation timestamp
    created_at: Optional[str] = None

        # Assigned driver information
    assigned_driver_id: Optional[str] = None
    assigned_driver_name: Optional[str] = None
    assigned_driver_rating: Optional[float] = None

    # Assigned vehicle information
    assigned_vehicle: Optional[str] = None
    assigned_vehicle_color: Optional[str] = None
    assigned_plate_number: Optional[str] = None

    # Driver arrival estimate
    driver_eta_minutes: Optional[int] = None

    def is_ready_for_planning(self) -> bool:
        """
        Return True when enough information exists
        to generate mobility options.
        """

        return (
            self.destination is not None
            and self.pickup_latitude is not None
            and self.pickup_longitude is not None
        )

    def is_ready_for_booking(self) -> bool:
        """
        Return True when the trip contains enough
        information to create a booking.
        """

        return (
            self.is_ready_for_planning()
            and self.service is not None
        )

    def set_booking_status(
        self,
        status: str,
    ) -> None:
        """
        Update the booking lifecycle state.
        """

        allowed_statuses = {
            "planning",
            "service_selected",
            "category_selected",
            "summary_ready",
            "booking_confirmed",
            "dispatch_pending",
            "driver_searching",
            "driver_assigned",
            "dispatch_failed",
        }

        if status not in allowed_statuses:
            raise ValueError(
                f"Invalid booking status: {status}"
            )

        self.booking_status = status