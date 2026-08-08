"""
HABESHAGO Pricing Event Service

Converts completed authoritative Pricing Platform
decisions into canonical HABESHAGO platform events.

Responsibilities:
- Build Pricing Quote events
- Build governed Pricing Adjustment events
- Build Financial Allocation events
- Publish pricing events through the shared Event Engine

This service observes completed pricing decisions.

It does not:
- calculate fares
- apply pricing adjustments
- calculate commission
- resolve pricing configuration
- modify pricing results
- persist settlement
"""

from app.constants.event_types import (
    EventType,
)

from app.models.event import (
    Event,
)

from app.pricing.adjustments import (
    AdjustedPricingResult,
)

from app.pricing.financial import (
    FinancialAllocation,
)

from app.pricing.models import (
    PricingQuote,
)

from app.services.event_engine import (
    publish_event,
)


def build_pricing_quote_issued_event(
    quote: PricingQuote,
) -> Event:
    """
    Build one canonical event for an authoritative issued
    PricingQuote.
    """

    if not isinstance(
        quote,
        PricingQuote,
    ):
        raise ValueError(
            "quote must be a PricingQuote."
        )

    return Event(
        event_type=(
            EventType.PRICING_QUOTE_ISSUED
        ),
        entity="pricing_quote",
        source="PricingPlatform",
        payload={
            "entity_id": quote.quote_id,
            "quote_id": quote.quote_id,
            "request_id": quote.request_id,
            "pricing_version": (
                quote.pricing_version
            ),
            "configuration_version": (
                quote.configuration_version
            ),
            "pricing_policy": (
                quote.pricing_policy
            ),
            "surge_policy": (
                quote.surge_policy
            ),
            "currency": (
                quote.breakdown.currency
            ),
            "total_fare": str(
                quote.breakdown.total_fare
            ),
            "quote_status": quote.status,
            "calculated_at": (
                quote.calculated_at.isoformat()
            ),
            "valid_until": (
                quote.valid_until.isoformat()
                if quote.valid_until
                is not None
                else None
            ),
        },
    )


def build_pricing_adjusted_event(
    *,
    pricing_quote_id: str,
    request_id: str,
    result: AdjustedPricingResult,
) -> Event:
    """
    Build one canonical event for a governed Pricing
    Adjustment result.
    """

    normalized_quote_id = str(
        pricing_quote_id or ""
    ).strip()

    normalized_request_id = str(
        request_id or ""
    ).strip()

    if not normalized_quote_id:
        raise ValueError(
            "pricing_quote_id cannot be empty."
        )

    if not normalized_request_id:
        raise ValueError(
            "request_id cannot be empty."
        )

    if not isinstance(
        result,
        AdjustedPricingResult,
    ):
        raise ValueError(
            (
                "result must be an "
                "AdjustedPricingResult."
            )
        )

    return Event(
        event_type=(
            EventType.PRICING_ADJUSTED
        ),
        entity="pricing_quote",
        source="PricingAdjustmentPlatform",
        payload={
            "entity_id": normalized_quote_id,
            "quote_id": normalized_quote_id,
            "request_id": normalized_request_id,
            "currency": (
                result
                .adjusted_breakdown
                .currency
            ),
            "core_total_fare": str(
                result
                .core_breakdown
                .total_fare
            ),
            "adjusted_total_fare": str(
                result
                .adjusted_breakdown
                .total_fare
            ),
            "surge_total": str(
                result
                .adjusted_breakdown
                .surge_total
            ),
            "discount_total": str(
                result
                .adjusted_breakdown
                .discount_total
            ),
            "adjustment_count": len(
                result.applied_adjustments
            ),
            "adjustment_references": tuple(
                adjustment.adjustment_reference
                for adjustment
                in result.applied_adjustments
            ),
            "policy_references": tuple(
                adjustment.policy_reference
                for adjustment
                in result.applied_adjustments
            ),
        },
    )


def build_financial_allocation_created_event(
    *,
    ride_id: int,
    pricing_quote_id: str,
    allocation: FinancialAllocation,
) -> Event:
    """
    Build one canonical event for an authoritative
    FinancialAllocation.
    """

    if (
        not isinstance(
            ride_id,
            int,
        )
        or isinstance(
            ride_id,
            bool,
        )
        or ride_id <= 0
    ):
        raise ValueError(
            "ride_id must be a positive integer."
        )

    normalized_quote_id = str(
        pricing_quote_id or ""
    ).strip()

    if not normalized_quote_id:
        raise ValueError(
            "pricing_quote_id cannot be empty."
        )

    if not isinstance(
        allocation,
        FinancialAllocation,
    ):
        raise ValueError(
            (
                "allocation must be a "
                "FinancialAllocation."
            )
        )

    return Event(
        event_type=(
            EventType.FINANCIAL_ALLOCATION_CREATED
        ),
        entity="ride_financial_allocation",
        source="PricingFinancialPlatform",
        payload={
            "entity_id": ride_id,
            "ride_id": ride_id,
            "quote_id": normalized_quote_id,
            "currency": allocation.currency,
            "passenger_fare": str(
                allocation.passenger_fare
            ),
            "commission_rate": str(
                allocation.commission_rate
            ),
            "commission_amount": str(
                allocation.commission_amount
            ),
            "driver_earnings": str(
                allocation.driver_earnings
            ),
            "commission_policy_version": (
                allocation
                .commission_policy_version
            ),
            "commission_policy_reference": (
                allocation
                .commission_policy_reference
            ),
        },
    )


def publish_pricing_quote_issued_event(
    quote: PricingQuote,
) -> Event:
    """
    Build and publish one Pricing Quote event.
    """

    event = build_pricing_quote_issued_event(
        quote
    )

    publish_event(
        event
    )

    return event


def publish_pricing_adjusted_event(
    *,
    pricing_quote_id: str,
    request_id: str,
    result: AdjustedPricingResult,
) -> Event:
    """
    Build and publish one Pricing Adjustment event.
    """

    event = build_pricing_adjusted_event(
        pricing_quote_id=pricing_quote_id,
        request_id=request_id,
        result=result,
    )

    publish_event(
        event
    )

    return event


def publish_financial_allocation_created_event(
    *,
    ride_id: int,
    pricing_quote_id: str,
    allocation: FinancialAllocation,
) -> Event:
    """
    Build and publish one Financial Allocation event.
    """

    event = (
        build_financial_allocation_created_event(
            ride_id=ride_id,
            pricing_quote_id=pricing_quote_id,
            allocation=allocation,
        )
    )

    publish_event(
        event
    )

    return event