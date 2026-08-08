"""
HABESHAGO Pricing Orchestrator

Provides the authoritative orchestration boundary for
the HABESHAGO Pricing Platform.

Commit #92 composes the authorities established by:

#87 - Pricing Configuration Platform
#88 - Core Decimal Pricing Engine
#89 - Pricing Adjustment Platform
#90 - Financial Allocation Platform

The orchestrator coordinates these authorities but does
not duplicate their business logic.

It does not:
- contain fare formulas
- hard-code fare values
- hard-code commission rates
- decide surge or discount policy
- mutate pricing configuration
- persist financial allocation
- publish platform events
- access Telegram or Mini App presentation code
- call AI
"""

from datetime import (
    datetime,
)

from app.pricing.adjustment_engine import (
    create_adjusted_pricing_result,
)

from app.pricing.adjustments import (
    PricingAdjustment,
)

from app.pricing.configuration_service import (
    get_effective_pricing_configuration,
)

from app.pricing.engine import (
    create_pricing_quote,
)

from app.pricing.exceptions import (
    PricingValidationError,
)

from app.pricing.financial import (
    CommissionPolicy,
)

from app.pricing.financial_engine import (
    allocate_financials,
)

from app.pricing.models import (
    PricingRequest,
)

from app.pricing.orchestration import (
    PricingOrchestrationResult,
)


def _require_aware_datetime(
    value,
    *,
    field_name: str,
) -> datetime:
    """
    Require one explicit timezone-aware orchestration
    timestamp.
    """

    if not isinstance(
        value,
        datetime,
    ):
        raise PricingValidationError(
            f"{field_name} must be datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PricingValidationError(
            (
                f"{field_name} must be "
                "timezone-aware."
            )
        )

    return value


def _validate_adjustments(
    adjustments,
) -> tuple[
    PricingAdjustment,
    ...,
]:
    """
    Require an immutable tuple of governed adjustments.
    """

    if not isinstance(
        adjustments,
        tuple,
    ):
        raise PricingValidationError(
            "adjustments must be a tuple."
        )

    for adjustment in adjustments:
        if not isinstance(
            adjustment,
            PricingAdjustment,
        ):
            raise PricingValidationError(
                (
                    "adjustments must contain only "
                    "PricingAdjustment values."
                )
            )

    return adjustments


def orchestrate_pricing(
    *,
    request: PricingRequest,
    quote_id: str,
    calculated_at: datetime,
    adjustments: tuple[
        PricingAdjustment,
        ...,
    ] = (),
    commission_policy: (
        CommissionPolicy | None
    ) = None,
    valid_until: datetime | None = None,
) -> PricingOrchestrationResult:
    """
    Execute one authoritative Pricing Platform workflow.

    Workflow:

        PricingRequest
            ↓
        resolve effective configuration
            ↓
        create authoritative core quote
            ↓
        apply supplied governed adjustments
            ↓
        optionally allocate commission / earnings
            ↓
        immutable PricingOrchestrationResult

    calculated_at is deliberately supplied by the caller
    and is also used as the configuration-resolution time.
    This prevents hidden system-clock state from changing
    which pricing configuration is selected.

    No events are published here. Event publication belongs
    to the outer production workflow after orchestration
    succeeds.
    """

    if not isinstance(
        request,
        PricingRequest,
    ):
        raise PricingValidationError(
            "request must be a PricingRequest."
        )

    if not isinstance(
        quote_id,
        str,
    ):
        raise PricingValidationError(
            "quote_id must be str."
        )

    normalized_quote_id = (
        quote_id.strip()
    )

    if not normalized_quote_id:
        raise PricingValidationError(
            "quote_id cannot be empty."
        )

    effective_time = (
        _require_aware_datetime(
            calculated_at,
            field_name="calculated_at",
        )
    )

    if valid_until is not None:
        _require_aware_datetime(
            valid_until,
            field_name="valid_until",
        )

        if valid_until <= effective_time:
            raise PricingValidationError(
                (
                    "valid_until must be later "
                    "than calculated_at."
                )
            )

    governed_adjustments = (
        _validate_adjustments(
            adjustments
        )
    )

    if (
        commission_policy is not None
        and not isinstance(
            commission_policy,
            CommissionPolicy,
        )
    ):
        raise PricingValidationError(
            (
                "commission_policy must be a "
                "CommissionPolicy or None."
            )
        )

    configuration = (
        get_effective_pricing_configuration(
            city=request.city,
            service_type=request.service_type,
            ride_category=request.ride_category,
            at_time=effective_time,
        )
    )

    quote = create_pricing_quote(
        request=request,
        configuration=configuration,
        quote_id=normalized_quote_id,
        calculated_at=effective_time,
        valid_until=valid_until,
    )

    adjusted_result = (
        create_adjusted_pricing_result(
            breakdown=quote.breakdown,
            adjustments=governed_adjustments,
        )
    )

    financial_allocation = None

    if commission_policy is not None:
        financial_allocation = (
            allocate_financials(
                pricing_result=adjusted_result,
                commission_policy=(
                    commission_policy
                ),
            )
        )

    return PricingOrchestrationResult(
        request=request,
        configuration=configuration,
        quote=quote,
        adjusted_result=adjusted_result,
        financial_allocation=(
            financial_allocation
        ),
    )