"""
HABESHAGO Pricing Financial Domain

Defines immutable Decimal-native financial allocation
contracts used between authoritative pricing and ride
settlement.

Commit #90 does not move money.

It defines:
- governed commission policy
- exact financial allocation
- validation of accounting invariants

Legacy ride settlement remains operational and will be
integrated through a compatibility bridge later in this
commit.
"""

from dataclasses import (
    dataclass,
)

from decimal import (
    Decimal,
)

from app.pricing.constants import (
    PricingCurrency,
)

from app.pricing.exceptions import (
    PricingValidationError,
)

from app.pricing.versions import (
    validate_version_identifier,
)


ZERO = Decimal("0.00")
ONE = Decimal("1.00")


def _require_text(
    value,
    *,
    field_name: str,
) -> str:
    """
    Require one non-empty text value.
    """

    if not isinstance(
        value,
        str,
    ):
        raise PricingValidationError(
            f"{field_name} must be str."
        )

    normalized = value.strip()

    if not normalized:
        raise PricingValidationError(
            f"{field_name} cannot be empty."
        )

    return normalized


def _require_decimal(
    value,
    *,
    field_name: str,
) -> Decimal:
    """
    Require one finite non-negative Decimal.
    """

    if not isinstance(
        value,
        Decimal,
    ):
        raise PricingValidationError(
            f"{field_name} must be Decimal."
        )

    if not value.is_finite():
        raise PricingValidationError(
            f"{field_name} must be finite."
        )

    if value < ZERO:
        raise PricingValidationError(
            f"{field_name} cannot be negative."
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class CommissionPolicy:
    """
    Immutable governed commission policy.

    The policy does not claim that any particular rate is
    legally required.

    It only represents the rate explicitly authorized by
    HABESHAGO policy for a financial allocation.
    """

    policy_version: str

    commission_rate: Decimal

    policy_reference: str

    currency: str = PricingCurrency.ETB

    def __post_init__(
        self,
    ) -> None:
        validate_version_identifier(
            self.policy_version,
            field_name="policy_version",
        )

        _require_decimal(
            self.commission_rate,
            field_name="commission_rate",
        )

        if self.commission_rate > ONE:
            raise PricingValidationError(
                (
                    "commission_rate cannot be "
                    "greater than 1."
                )
            )

        _require_text(
            self.policy_reference,
            field_name="policy_reference",
        )

        if (
            self.currency
            not in PricingCurrency.ALL
        ):
            raise PricingValidationError(
                (
                    "Unsupported currency: "
                    f"{self.currency}"
                )
            )


@dataclass(
    frozen=True,
    slots=True,
)
class FinancialAllocation:
    """
    Immutable exact allocation of one authoritative fare.

    Accounting invariant:

        passenger_fare
        =
        commission_amount
        +
        driver_earnings
    """

    passenger_fare: Decimal

    commission_rate: Decimal

    commission_amount: Decimal

    driver_earnings: Decimal

    commission_policy_version: str

    commission_policy_reference: str

    currency: str = PricingCurrency.ETB

    def __post_init__(
        self,
    ) -> None:
        _require_decimal(
            self.passenger_fare,
            field_name="passenger_fare",
        )

        _require_decimal(
            self.commission_rate,
            field_name="commission_rate",
        )

        _require_decimal(
            self.commission_amount,
            field_name="commission_amount",
        )

        _require_decimal(
            self.driver_earnings,
            field_name="driver_earnings",
        )

        if self.commission_rate > ONE:
            raise PricingValidationError(
                (
                    "commission_rate cannot be "
                    "greater than 1."
                )
            )

        validate_version_identifier(
            self.commission_policy_version,
            field_name=(
                "commission_policy_version"
            ),
        )

        _require_text(
            self.commission_policy_reference,
            field_name=(
                "commission_policy_reference"
            ),
        )

        if (
            self.currency
            not in PricingCurrency.ALL
        ):
            raise PricingValidationError(
                (
                    "Unsupported currency: "
                    f"{self.currency}"
                )
            )

        if (
            self.commission_amount
            > self.passenger_fare
        ):
            raise PricingValidationError(
                (
                    "commission_amount cannot exceed "
                    "passenger_fare."
                )
            )

        if (
            self.driver_earnings
            > self.passenger_fare
        ):
            raise PricingValidationError(
                (
                    "driver_earnings cannot exceed "
                    "passenger_fare."
                )
            )

        if (
            self.commission_amount
            + self.driver_earnings
            != self.passenger_fare
        ):
            raise PricingValidationError(
                (
                    "Financial allocation invariant "
                    "failed: commission_amount + "
                    "driver_earnings must exactly "
                    "equal passenger_fare."
                )
            )