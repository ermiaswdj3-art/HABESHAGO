"""
HABESHAGO Ride Settlement Model

Defines the canonical financial settlement contract for
completed HABESHAGO rides.

A settlement becomes authoritative only after a ride
successfully completes.
"""

from dataclasses import dataclass
from typing import Optional


SETTLEMENT_STATUSES = {
    "not_settled",
    "settled",
    "reversed",
}


@dataclass(slots=True)
class RideSettlement:
    """
    Represents the financial settlement of one ride.
    """

    ride_id: int

    driver_id: int

    fare: float

    service_type: str

    commission_rate: float

    commission_amount: float

    driver_earnings: float

    settlement_status: str = "not_settled"

    settled_at: Optional[str] = None

    settlement_reference: Optional[str] = None

    def validate(self) -> None:
        """
        Validate the canonical settlement contract.
        """

        if self.ride_id <= 0:
            raise ValueError(
                "ride_id must be greater than zero."
            )

        if self.driver_id <= 0:
            raise ValueError(
                "driver_id must be greater than zero."
            )

        if self.fare < 0:
            raise ValueError(
                "fare cannot be negative."
            )

        if (
            self.commission_rate < 0
            or self.commission_rate > 1
        ):
            raise ValueError(
                "commission_rate must be between "
                "0 and 1."
            )

        if self.commission_amount < 0:
            raise ValueError(
                "commission_amount cannot be negative."
            )

        if self.driver_earnings < 0:
            raise ValueError(
                "driver_earnings cannot be negative."
            )

        if (
            self.settlement_status
            not in SETTLEMENT_STATUSES
        ):
            raise ValueError(
                "Invalid settlement status: "
                f"{self.settlement_status}"
            )

        expected_driver_earnings = round(
            self.fare
            - self.commission_amount,
            2,
        )

        if (
            abs(
                self.driver_earnings
                - expected_driver_earnings
            )
            > 0.01
        ):
            raise ValueError(
                "driver_earnings must equal fare "
                "minus commission_amount."
            )

        if self.settlement_status == "settled":
            if not self.settled_at:
                raise ValueError(
                    "A settled ride requires settled_at."
                )

            if not self.settlement_reference:
                raise ValueError(
                    "A settled ride requires a "
                    "settlement reference."
                )

    def is_settled(self) -> bool:
        """
        Return True when settlement is complete.
        """

        return (
            self.settlement_status
            == "settled"
        )

    def is_reversed(self) -> bool:
        """
        Return True when settlement was reversed.
        """

        return (
            self.settlement_status
            == "reversed"
        )