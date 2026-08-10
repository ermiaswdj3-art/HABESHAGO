"""
HABESHAGO Ride Commerce Context

Defines the immutable operational context required to
connect one authoritative HABESHAGO ride to Pricing
and Commerce.

The context identifies the ride, passenger and selected
payment method.

It does not:
- calculate fares
- calculate commission
- calculate driver earnings
- create payment amounts
- execute payments
- modify ride state
"""

from dataclasses import dataclass


def _require_positive_integer(
    value: int,
    *,
    field_name: str,
) -> None:
    """
    Require a positive integer identifier.
    """

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value <= 0
    ):
        raise ValueError(
            f"{field_name} must be a positive integer."
        )


def _require_text(
    value: str,
    *,
    field_name: str,
) -> None:
    """
    Require non-empty text.
    """

    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise ValueError(
            f"{field_name} cannot be empty."
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RideCommerceContext:
    """
    Immutable identity and payment-selection context for
    one Ride -> Pricing -> Commerce workflow.

    Financial values deliberately do not belong here.
    They must originate from the authoritative Pricing
    Platform.
    """

    ride_id: int

    passenger_id: int

    payment_method: str

    def __post_init__(
        self,
    ) -> None:
        _require_positive_integer(
            self.ride_id,
            field_name="ride_id",
        )

        _require_positive_integer(
            self.passenger_id,
            field_name="passenger_id",
        )

        _require_text(
            self.payment_method,
            field_name="payment_method",
        )