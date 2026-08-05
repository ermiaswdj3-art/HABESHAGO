"""
HABESHAGO Driver Operational State Model

Defines the canonical operational lifecycle contract
for HABESHAGO drivers.

The Telegram Bot, Telegram Mini App, future native apps,
Dispatch Platform, and Admin Platform must all read and
write the same driver operational state.
"""

from dataclasses import dataclass
from typing import Optional


DRIVER_OPERATIONAL_STATUSES = {
    "offline",
    "available",
    "unavailable",
}


@dataclass(slots=True)
class DriverOperationalState:
    """
    Represents one driver's canonical operational state.
    """

    driver_id: int

    operational_status: str

    is_online: bool

    is_available: bool

    status_updated_at: Optional[str] = None

    def validate(self) -> None:
        """
        Validate lifecycle consistency.
        """

        if self.driver_id <= 0:
            raise ValueError(
                "driver_id must be greater than zero."
            )

        if (
            self.operational_status
            not in DRIVER_OPERATIONAL_STATUSES
        ):
            raise ValueError(
                "Invalid driver operational status: "
                f"{self.operational_status}"
            )

        expected_flags = {
            "offline": (
                False,
                False,
            ),
            "available": (
                True,
                True,
            ),
            "unavailable": (
                True,
                False,
            ),
        }

        expected_online, expected_available = (
            expected_flags[
                self.operational_status
            ]
        )

        if self.is_online != expected_online:
            raise ValueError(
                "is_online is inconsistent with "
                "operational_status."
            )

        if (
            self.is_available
            != expected_available
        ):
            raise ValueError(
                "is_available is inconsistent with "
                "operational_status."
            )

    def can_receive_ride_offers(self) -> bool:
        """
        Return True when the driver may receive offers.
        """

        return (
            self.operational_status
            == "available"
        )

    def is_offline(self) -> bool:
        """
        Return True when the driver is offline.
        """

        return (
            self.operational_status
            == "offline"
        )