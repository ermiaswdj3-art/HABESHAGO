"""
HABESHAGO Trip Model

This module defines the canonical Trip object shared across
the entire HABESHAGO mobility platform.

Every service (Ride, Transit, Logistics, AI, Wallet, Rewards)
will work with this same model.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Trip:
    # Canonical shared Ride Platform identity
    canonical_ride_id: Optional[int] = None
    canonical_passenger_id: Optional[int] = None
    canonical_driver_id: Optional[int] = None
    # Destination chosen by the passenger
    destination: Optional[str] = None
    destination_latitude: Optional[float] = None
    destination_longitude: Optional[float] = None

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

    # HABESHAGO recommendation
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

    # Trip lifecycle
    trip_started_at: Optional[str] = None
    trip_completed_at: Optional[str] = None
    trip_progress_percent: int = 0
    destination_reached: bool = False

    # Pickup verification
    pickup_pin: Optional[str] = None
    pickup_pin_generated_at: Optional[str] = None
    pickup_pin_verified: bool = False
    pickup_verified_at: Optional[str] = None
    pickup_verification_attempts: int = 0

    # Final pricing
    final_fare: Optional[float] = None
    fare_currency: str = "ETB"
    fare_breakdown: dict[str, float] = field(
        default_factory=dict
    )

    # Payment platform
    payment_method: Optional[str] = None
    payment_status: str = "not_started"
    payment_transaction_id: Optional[str] = None
    payment_completed_at: Optional[str] = None

    # Receipt
    receipt_id: Optional[str] = None

    def is_ready_for_planning(self) -> bool:
        """
        Return True when enough canonical location context
        exists to generate mobility options.

        Both pickup and destination coordinates are required
        for authoritative ride planning.
        """

        return (
            self.destination is not None
            and self.destination_latitude is not None
            and self.destination_longitude is not None
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

    def is_ready_to_start_trip(self) -> bool:
        """
        Return True when the passenger has been
        securely verified and the ride may begin.
        """

        return self.booking_status == "ready_to_start"

    def is_ready_for_pickup_verification(self) -> bool:
        """
        Return True when a driver has arrived and the
        trip can begin pickup verification.
        """

        return (
            self.booking_status
            in {
                "driver_arrived",
                "pickup_verification_pending",
            }
            and self.assigned_driver_id is not None
            and self.pickup_pin is not None
        )

    def is_ready_for_payment(self) -> bool:
        """
        Return True when the completed trip has a
        calculated final fare.
        """

        return (
            self.booking_status == "trip_completed"
            and self.final_fare is not None
            and self.final_fare >= 0
        )

    def set_booking_status(
        self,
        status: str,
    ) -> None:
        """
        Update the booking and trip lifecycle state.
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
            "driver_arriving",
            "driver_arrived",
            "pickup_verification_pending",
            "passenger_verified",
            "ready_to_start",
            "trip_started",
            "trip_in_progress",
            "arriving_destination",
            "trip_completed",
            "dispatch_failed",
        }

        if status not in allowed_statuses:
            raise ValueError(
                f"Invalid booking status: {status}"
            )

        self.booking_status = status

    def set_payment_status(
        self,
        status: str,
    ) -> None:
        """
        Update the payment lifecycle state.
        """

        allowed_statuses = {
            "not_started",
            "payment_pending",
            "payment_method_selected",
            "payment_processing",
            "payment_completed",
            "payment_failed",
            "payment_refunded",
        }

        if status not in allowed_statuses:
            raise ValueError(
                f"Invalid payment status: {status}"
            )

        self.payment_status = status