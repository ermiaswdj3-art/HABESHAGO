"""
HABESHAGO Pricing Financial Allocation Engine

Converts an authoritative adjusted pricing result into an
exact Decimal financial allocation under an explicitly
supplied CommissionPolicy.

The engine does not:
- resolve commission policy
- hard-code commission rates
- access the database
- settle rides
- generate settlement references
- access the system clock
- move money
- publish events
- call Telegram
- call AI

Given identical inputs, the FinancialAllocation is
identical.
"""

from decimal import (
    Decimal,
)

from app.pricing.adjustments import (
    AdjustedPricingResult,
)

from app.pricing.exceptions import (
    PricingCalculationError,
)

from app.pricing.financial import (
    CommissionPolicy,
    FinancialAllocation,
)


ZERO = Decimal("0.00")


def _validate_allocation_inputs(
    *,
    pricing_result: AdjustedPricingResult,
    commission_policy: CommissionPolicy,
) -> None:
    """
    Validate the financial allocation boundary.
    """

    if not isinstance(
        pricing_result,
        AdjustedPricingResult,
    ):
        raise PricingCalculationError(
            (
                "pricing_result must be an "
                "AdjustedPricingResult."
            )
        )

    if not isinstance(
        commission_policy,
        CommissionPolicy,
    ):
        raise PricingCalculationError(
            (
                "commission_policy must be a "
                "CommissionPolicy."
            )
        )

    if (
        pricing_result.adjusted_breakdown.currency
        != commission_policy.currency
    ):
        raise PricingCalculationError(
            (
                "Commission policy currency does not "
                "match authoritative pricing currency."
            )
        )


def allocate_financials(
    *,
    pricing_result: AdjustedPricingResult,
    commission_policy: CommissionPolicy,
) -> FinancialAllocation:
    """
    Allocate one authoritative passenger fare between
    HABESHAGO commission and driver earnings.

    The authoritative passenger fare comes only from the
    final adjusted FareBreakdown.

    Formula:

        commission_amount
            =
        passenger_fare * commission_rate

        driver_earnings
            =
        passenger_fare - commission_amount

    No monetary rounding is introduced here.

    Exact Decimal arithmetic is preserved so future
    commission-rounding policy can remain explicit and
    governed rather than hidden inside this engine.
    """

    _validate_allocation_inputs(
        pricing_result=pricing_result,
        commission_policy=commission_policy,
    )

    passenger_fare = (
        pricing_result
        .adjusted_breakdown
        .total_fare
    )

    commission_amount = (
        passenger_fare
        * commission_policy.commission_rate
    )

    driver_earnings = (
        passenger_fare
        - commission_amount
    )

    if (
        commission_amount < ZERO
        or driver_earnings < ZERO
    ):
        raise PricingCalculationError(
            (
                "Financial allocation produced a "
                "negative monetary value."
            )
        )

    return FinancialAllocation(
        passenger_fare=passenger_fare,
        commission_rate=(
            commission_policy.commission_rate
        ),
        commission_amount=commission_amount,
        driver_earnings=driver_earnings,
        commission_policy_version=(
            commission_policy.policy_version
        ),
        commission_policy_reference=(
            commission_policy.policy_reference
        ),
        currency=commission_policy.currency,
    )