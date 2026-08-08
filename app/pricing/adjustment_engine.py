"""
HABESHAGO Pricing Adjustment Engine

Applies already-authorized governed pricing adjustments
to a core FareBreakdown produced by the Core Decimal
Pricing Engine.

This engine does not decide whether an adjustment should
exist. It only applies explicit PricingAdjustment values
supplied by the caller.

The engine has no:
- database access
- configuration lookup
- system clock access
- network access
- Telegram dependency
- Mini App dependency
- persistence
- event publication
- commission logic
- settlement logic
- AI dependency
- surge decision logic
- promotion eligibility logic

Given identical inputs, the adjusted FareBreakdown is
identical.
"""

from decimal import (
    Decimal,
)

from app.pricing.adjustments import (
    AdjustedPricingResult,
    PricingAdjustment,
    PricingAdjustmentType,
)

from app.pricing.constants import (
    PricingComponentType,
)

from app.pricing.exceptions import (
    PricingCalculationError,
)

from app.pricing.models import (
    FareBreakdown,
    PricingComponent,
)


ZERO = Decimal("0.00")


def _validate_adjustment_inputs(
    *,
    breakdown: FareBreakdown,
    adjustments: tuple[
        PricingAdjustment,
        ...,
    ],
) -> None:
    """
    Validate the adjustment application boundary.
    """

    if not isinstance(
        breakdown,
        FareBreakdown,
    ):
        raise PricingCalculationError(
            "breakdown must be a FareBreakdown."
        )

    if not isinstance(
        adjustments,
        tuple,
    ):
        raise PricingCalculationError(
            "adjustments must be a tuple."
        )

        if (
            breakdown.surge_total != ZERO
            or breakdown.discount_total != ZERO
        ):
            raise PricingCalculationError(
                (
                    "Pricing adjustments can be applied "
                    "only to an unadjusted core "
                    "FareBreakdown."
                )
            )

    existing_adjustment_components = [
        component
        for component in breakdown.components
        if component.component_type
        in {
            PricingComponentType.SURGE,
            PricingComponentType.DISCOUNT,
        }
    ]

    if existing_adjustment_components:
        raise PricingCalculationError(
            (
                "Pricing adjustments can be applied "
                "only to a FareBreakdown without "
                "existing surge or discount "
                "components."
            )
        )

    seen_references: set[str] = set()
    seen_sequences: set[int] = set()

    for adjustment in adjustments:
        if not isinstance(
            adjustment,
            PricingAdjustment,
        ):
            raise PricingCalculationError(
                (
                    "adjustments must contain "
                    "PricingAdjustment values."
                )
            )

        if (
            adjustment.currency
            != breakdown.currency
        ):
            raise PricingCalculationError(
                (
                    "Pricing adjustment currency "
                    "does not match FareBreakdown "
                    "currency."
                )
            )

        if (
            adjustment.adjustment_reference
            in seen_references
        ):
            raise PricingCalculationError(
                (
                    "Duplicate pricing adjustment "
                    "reference: "
                    f"{adjustment.adjustment_reference}"
                )
            )

        if (
            adjustment.sequence
            in seen_sequences
        ):
            raise PricingCalculationError(
                (
                    "Duplicate pricing adjustment "
                    "sequence: "
                    f"{adjustment.sequence}"
                )
            )

        seen_references.add(
            adjustment.adjustment_reference
        )

        seen_sequences.add(
            adjustment.sequence
        )


def _ordered_adjustments(
    adjustments: tuple[
        PricingAdjustment,
        ...,
    ],
) -> tuple[
    PricingAdjustment,
    ...,
]:
    """
    Return adjustments in deterministic application order.
    """

    return tuple(
        sorted(
            adjustments,
            key=lambda adjustment: (
                adjustment.sequence,
                adjustment.adjustment_reference,
            ),
        )
    )


def apply_pricing_adjustments(
    *,
    breakdown: FareBreakdown,
    adjustments: tuple[
        PricingAdjustment,
        ...,
    ],
) -> FareBreakdown:
    """
    Apply explicit governed adjustments to one core
    FareBreakdown.

    Rules:

        surcharge:
            increases the fare

        discount:
            decreases the fare but can never make the
            authoritative fare negative

    Adjustments are applied in deterministic sequence
    order.

    The original FareBreakdown is never mutated.
    """

    _validate_adjustment_inputs(
        breakdown=breakdown,
        adjustments=adjustments,
    )

    if not adjustments:
        return breakdown

    running_total = breakdown.total_fare

    surge_total = ZERO
    discount_total = ZERO

    adjustment_components = []

    for adjustment in _ordered_adjustments(
        adjustments
    ):
        if (
            adjustment.adjustment_type
            == PricingAdjustmentType.SURCHARGE
        ):
            applied_amount = adjustment.amount

            running_total += applied_amount
            surge_total += applied_amount

            adjustment_components.append(
                PricingComponent(
                    component_type=(
                        PricingComponentType.SURGE
                    ),
                    amount=applied_amount,
                    description=(
                        f"{adjustment.reason} "
                        "["
                        f"{adjustment.policy_reference}"
                        "]"
                    ),
                )
            )

        elif (
            adjustment.adjustment_type
            == PricingAdjustmentType.DISCOUNT
        ):
            applied_amount = min(
                adjustment.amount,
                running_total,
            )

            running_total -= applied_amount
            discount_total += applied_amount

            adjustment_components.append(
                PricingComponent(
                    component_type=(
                        PricingComponentType.DISCOUNT
                    ),
                    amount=applied_amount,
                    description=(
                        f"{adjustment.reason} "
                        "["
                        f"{adjustment.policy_reference}"
                        "]"
                    ),
                )
            )

        else:
            raise PricingCalculationError(
                (
                    "Unsupported pricing adjustment "
                    "type: "
                    f"{adjustment.adjustment_type}"
                )
            )

    if running_total < ZERO:
        raise PricingCalculationError(
            (
                "Adjusted pricing total cannot "
                "be negative."
            )
        )

    return FareBreakdown(
        currency=breakdown.currency,
        components=(
            breakdown.components
            + tuple(
                adjustment_components
            )
        ),
        subtotal=breakdown.subtotal,
        total_fare=running_total,
        minimum_fare=breakdown.minimum_fare,
        discount_total=(
            breakdown.discount_total
            + discount_total
        ),
        surge_total=(
            breakdown.surge_total
            + surge_total
        ),
    )

def create_adjusted_pricing_result(
    *,
    breakdown: FareBreakdown,
    adjustments: tuple[
        PricingAdjustment,
        ...,
    ],
) -> AdjustedPricingResult:
    """
    Apply governed pricing adjustments and preserve the
    complete deterministic adjustment provenance.

    The stored adjustment order is the same canonical
    sequence order used for monetary application.
    """

    adjusted_breakdown = (
        apply_pricing_adjustments(
            breakdown=breakdown,
            adjustments=adjustments,
        )
    )

    ordered_adjustments = (
        _ordered_adjustments(
            adjustments
        )
    )

    return AdjustedPricingResult(
        core_breakdown=breakdown,
        adjusted_breakdown=(
            adjusted_breakdown
        ),
        applied_adjustments=(
            ordered_adjustments
        ),
    )