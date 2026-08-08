"""
HABESHAGO Pricing Adjustment Domain

Defines immutable governed pricing adjustments applied
after the Core Decimal Pricing Engine has produced its
authoritative core FareBreakdown.

Commit #89 keeps pricing adjustments separate from the
pure core calculation performed by app.pricing.engine.

This module also defines the immutable result that
preserves the complete provenance of applied adjustments.

This module does not:
- calculate the core fare
- resolve pricing configuration
- access the database
- access the system clock
- publish events
- perform settlement or commission
- call AI
- depend on Telegram or the Mini App
"""

from dataclasses import (
    dataclass,
)

from decimal import (
    Decimal,
)

from app.pricing.constants import (
    PricingComponentType,
    PricingCurrency,
)

from app.pricing.exceptions import (
    PricingValidationError,
)

from app.pricing.models import (
    FareBreakdown,
)


ZERO = Decimal("0.00")


class PricingAdjustmentType:
    """
    Canonical adjustment directions.

    SURCHARGE increases the authoritative fare.

    DISCOUNT decreases the authoritative fare.
    """

    SURCHARGE = "surcharge"

    DISCOUNT = "discount"

    ALL = {
        SURCHARGE,
        DISCOUNT,
    }


class PricingAdjustmentSource:
    """
    Canonical authority that caused an adjustment.
    """

    PRICING_POLICY = "pricing_policy"

    SURGE_POLICY = "surge_policy"

    PROMOTION_POLICY = "promotion_policy"

    ADMIN_POLICY = "admin_policy"

    SYSTEM_POLICY = "system_policy"

    ALL = {
        PRICING_POLICY,
        SURGE_POLICY,
        PROMOTION_POLICY,
        ADMIN_POLICY,
        SYSTEM_POLICY,
    }


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


def _require_choice(
    value,
    *,
    field_name: str,
    allowed_values: set[str],
) -> str:
    """
    Require one canonical vocabulary value.
    """

    normalized = _require_text(
        value,
        field_name=field_name,
    )

    if normalized not in allowed_values:
        raise PricingValidationError(
            (
                f"Unsupported {field_name}: "
                f"{normalized}"
            )
        )

    return normalized


def _require_decimal(
    value,
    *,
    field_name: str,
    allow_zero: bool = True,
) -> Decimal:
    """
    Require one exact non-negative finite Decimal.
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

    if (
        not allow_zero
        and value == ZERO
    ):
        raise PricingValidationError(
            f"{field_name} must be greater than zero."
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class PricingAdjustment:
    """
    Immutable instruction for one governed pricing
    adjustment.

    amount is always stored as a positive Decimal.

    adjustment_type determines direction:

        surcharge -> increases fare
        discount  -> decreases fare

    adjustment_reference uniquely identifies the decision
    that produced this adjustment.

    policy_reference identifies the governing policy,
    promotion, rule, campaign or administrative authority
    responsible for the decision.

    sequence provides deterministic ordering when several
    adjustments apply to the same pricing result.
    """

    adjustment_reference: str

    adjustment_type: str

    component_type: str

    amount: Decimal

    source: str

    reason: str

    policy_reference: str

    sequence: int

    currency: str = PricingCurrency.ETB

    def __post_init__(
        self,
    ) -> None:
        _require_text(
            self.adjustment_reference,
            field_name=(
                "adjustment_reference"
            ),
        )

        _require_choice(
            self.adjustment_type,
            field_name="adjustment_type",
            allowed_values=(
                PricingAdjustmentType.ALL
            ),
        )

        _require_choice(
            self.component_type,
            field_name="component_type",
            allowed_values={
                PricingComponentType.SURGE,
                PricingComponentType.DISCOUNT,
            },
        )

        _require_decimal(
            self.amount,
            field_name="amount",
            allow_zero=False,
        )

        _require_choice(
            self.source,
            field_name="source",
            allowed_values=(
                PricingAdjustmentSource.ALL
            ),
        )

        _require_text(
            self.reason,
            field_name="reason",
        )

        _require_text(
            self.policy_reference,
            field_name="policy_reference",
        )

        _require_choice(
            self.currency,
            field_name="currency",
            allowed_values=(
                PricingCurrency.ALL
            ),
        )

        if (
            not isinstance(
                self.sequence,
                int,
            )
            or isinstance(
                self.sequence,
                bool,
            )
        ):
            raise PricingValidationError(
                "sequence must be int."
            )

        if self.sequence < 0:
            raise PricingValidationError(
                "sequence cannot be negative."
            )

        if (
            self.adjustment_type
            == PricingAdjustmentType.SURCHARGE
            and self.component_type
            != PricingComponentType.SURGE
        ):
            raise PricingValidationError(
                (
                    "Surcharge adjustments must use "
                    "component_type surge."
                )
            )

        if (
            self.adjustment_type
            == PricingAdjustmentType.DISCOUNT
            and self.component_type
            != PricingComponentType.DISCOUNT
        ):
            raise PricingValidationError(
                (
                    "Discount adjustments must use "
                    "component_type discount."
                )
            )


@dataclass(
    frozen=True,
    slots=True,
)
class AdjustedPricingResult:
    """
    Immutable result of applying governed pricing
    adjustments to one core FareBreakdown.

    The result preserves:
    - the original core breakdown
    - the final adjusted breakdown
    - the exact ordered adjustments that were applied

    This makes the pricing decision reproducible and
    auditable without relying on presentation text.
    """

    core_breakdown: FareBreakdown

    adjusted_breakdown: FareBreakdown

    applied_adjustments: tuple[
        PricingAdjustment,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.core_breakdown,
            FareBreakdown,
        ):
            raise PricingValidationError(
                (
                    "core_breakdown must be a "
                    "FareBreakdown."
                )
            )

        if not isinstance(
            self.adjusted_breakdown,
            FareBreakdown,
        ):
            raise PricingValidationError(
                (
                    "adjusted_breakdown must be a "
                    "FareBreakdown."
                )
            )

        if not isinstance(
            self.applied_adjustments,
            tuple,
        ):
            raise PricingValidationError(
                (
                    "applied_adjustments must be "
                    "a tuple."
                )
            )

        for adjustment in (
            self.applied_adjustments
        ):
            if not isinstance(
                adjustment,
                PricingAdjustment,
            ):
                raise PricingValidationError(
                    (
                        "applied_adjustments must "
                        "contain PricingAdjustment "
                        "values."
                    )
                )

        if (
            self.core_breakdown.currency
            != self.adjusted_breakdown.currency
        ):
            raise PricingValidationError(
                (
                    "Core and adjusted breakdown "
                    "currencies must match."
                )
            )