"""
HABESHAGO Vehicle Model

Defines the canonical vehicle contract shared across
driver registration, verification, dispatch, pricing,
admin operations, logistics, and future fleet services.
"""

from dataclasses import dataclass
from typing import Optional


VEHICLE_TYPES = {
    "fuel_car",
    "electric_car",
    "motorcycle",
    "legacy",
}

VEHICLE_CATEGORIES = {
    "standard",
    "premium",
    "utility",
    "motorcycle",
    "logistics",
}

VEHICLE_VERIFICATION_STATUSES = {
    "pending",
    "verified",
    "rejected",
    "suspended",
}


@dataclass(slots=True)
class Vehicle:
    """
    Represents one HABESHAGO vehicle.
    """

    vehicle_id: Optional[int]

    driver_id: int

    vehicle_type: str

    brand: str

    model: str

    manufacturing_year: int

    color: str

    plate_number: str

    plate_type: Optional[str] = None

    plate_region: Optional[str] = None

    category: str = "standard"

    verification_status: str = "pending"

    is_active: bool = True

    created_at: Optional[str] = None

    updated_at: Optional[str] = None

    def validate(self) -> None:
        """
        Validate the canonical vehicle contract.
        """

        if self.vehicle_type not in VEHICLE_TYPES:
            raise ValueError(
                f"Invalid vehicle type: {self.vehicle_type}"
            )

        if self.category not in VEHICLE_CATEGORIES:
            raise ValueError(
                f"Invalid vehicle category: {self.category}"
            )

        if (
            self.verification_status
            not in VEHICLE_VERIFICATION_STATUSES
        ):
            raise ValueError(
                "Invalid vehicle verification status: "
                f"{self.verification_status}"
            )

        if not self.brand.strip():
            raise ValueError(
                "Vehicle brand is required."
            )

        if not self.model.strip():
            raise ValueError(
                "Vehicle model is required."
            )

        if not self.color.strip():
            raise ValueError(
                "Vehicle color is required."
            )

        if not self.plate_number.strip():
            raise ValueError(
                "Vehicle plate number is required."
            )

        if self.manufacturing_year < 1900:
            raise ValueError(
                "Vehicle manufacturing year is invalid."
            )

    @property
    def display_name(self) -> str:
        """
        Return the human-readable vehicle name.
        """

        return (
            f"{self.brand.strip()} "
            f"{self.model.strip()}"
        ).strip()

    def is_verified(self) -> bool:
        """
        Return True when the vehicle is verified.
        """

        return (
            self.verification_status
            == "verified"
        )

    def can_be_used_for_operations(self) -> bool:
        """
        Return True when the vehicle is active and verified.
        """

        return (
            self.is_active
            and self.is_verified()
        )