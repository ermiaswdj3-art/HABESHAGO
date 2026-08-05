"""
HABESHAGO Ride Offer Model

Defines the canonical driver ride-offer contract shared by
the Telegram Bot, Telegram Mini App, future native apps,
Dispatch Platform, Notification Platform, and Admin Platform.
"""

from dataclasses import dataclass
from typing import Optional

from app.constants.offer_status import (
    ACCEPTED,
    ALL_OFFER_STATUSES,
    CANCELLED,
    EXPIRED,
    PENDING,
    REJECTED,
)


@dataclass(slots=True)
class RideOffer:
    """
    Represents one canonical offer made to one driver.
    """

    offer_id: Optional[int]

    offer_reference: str

    passenger_id: int

    driver_id: int

    pickup_latitude: float

    pickup_longitude: float

    destination_latitude: float

    destination_longitude: float

    distance: float

    pickup_distance: float

    pickup_eta: int

    trip_eta: int

    fare: float

    payment_method: str

    service_type: str

    status: str = PENDING

    accepted_ride_id: Optional[int] = None

    created_at: Optional[str] = None

    expires_at: Optional[str] = None

    accepted_at: Optional[str] = None

    rejected_at: Optional[str] = None

    expired_at: Optional[str] = None

    cancelled_at: Optional[str] = None

    def validate(self) -> None:
        """
        Validate the canonical Ride Offer contract.
        """

        if self.offer_id is not None and self.offer_id <= 0:
            raise ValueError(
                "offer_id must be greater than zero."
            )

        if not self.offer_reference.strip():
            raise ValueError(
                "offer_reference is required."
            )

        if self.passenger_id <= 0:
            raise ValueError(
                "passenger_id must be greater than zero."
            )

        if self.driver_id <= 0:
            raise ValueError(
                "driver_id must be greater than zero."
            )

        if self.distance < 0:
            raise ValueError(
                "distance cannot be negative."
            )

        if self.pickup_distance < 0:
            raise ValueError(
                "pickup_distance cannot be negative."
            )

        if self.pickup_eta < 0:
            raise ValueError(
                "pickup_eta cannot be negative."
            )

        if self.trip_eta < 0:
            raise ValueError(
                "trip_eta cannot be negative."
            )

        if self.fare < 0:
            raise ValueError(
                "fare cannot be negative."
            )

        if self.status not in ALL_OFFER_STATUSES:
            raise ValueError(
                f"Invalid ride-offer status: {self.status}"
            )

        if self.status == ACCEPTED:
            if self.accepted_ride_id is None:
                raise ValueError(
                    "An accepted offer requires "
                    "accepted_ride_id."
                )

            if not self.accepted_at:
                raise ValueError(
                    "An accepted offer requires accepted_at."
                )

        timestamp_requirements = {
            REJECTED: self.rejected_at,
            EXPIRED: self.expired_at,
            CANCELLED: self.cancelled_at,
        }

        required_timestamp = timestamp_requirements.get(
            self.status
        )

        if (
            self.status in timestamp_requirements
            and not required_timestamp
        ):
            raise ValueError(
                f"{self.status} requires its lifecycle "
                "timestamp."
            )

    def is_pending(self) -> bool:
        """
        Return True while the driver may respond.
        """

        return self.status == PENDING

    def is_terminal(self) -> bool:
        """
        Return True once no further response is allowed.
        """

        return self.status in {
            ACCEPTED,
            REJECTED,
            EXPIRED,
            CANCELLED,
        }

    def can_be_accepted(self) -> bool:
        """
        Return True when the offer may still be accepted.
        """

        return (
            self.status == PENDING
            and self.accepted_ride_id is None
        )