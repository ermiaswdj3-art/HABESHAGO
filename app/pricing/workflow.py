"""
HABESHAGO Pricing Production Workflow

Provides the production-facing application boundary around
the authoritative Pricing Orchestrator.

Responsibilities:
- Execute one authoritative pricing orchestration
- Publish Pricing Platform events only after successful
  orchestration
- Return both the authoritative result and emitted events

This workflow does not:
- calculate fares
- resolve pricing rules itself
- apply adjustment mathematics
- calculate commission
- persist financial settlement
- depend on Telegram or Mini App presentation code
"""

from dataclasses import (
    dataclass,
)

from datetime import (
    datetime,
)

from app.models.event import (
    Event,
)

from app.pricing.adjustments import (
    PricingAdjustment,
)

from app.pricing.financial import (
    CommissionPolicy,
)

from app.pricing.models import (
    PricingRequest,
)

from app.pricing.orchestration import (
    PricingOrchestrationResult,
)

from app.pricing.orchestrator import (
    orchestrate_pricing,
)

from app.services.pricing_event_service import (
    publish_financial_allocation_created_event,
    publish_pricing_adjusted_event,
    publish_pricing_quote_issued_event,
)


@dataclass(
    frozen=True,
    slots=True,
)
class PricingWorkflowResult:
    """
    Immutable result of one production pricing workflow.

    events contains the exact canonical platform events
    emitted after successful orchestration.
    """

    pricing: PricingOrchestrationResult

    events: tuple[
        Event,
        ...,
    ]


def execute_pricing_workflow(
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
    ride_id: int | None = None,
) -> PricingWorkflowResult:
    """
    Execute one production-facing pricing workflow.

    Events are published only after the complete
    orchestration succeeds.

    Event order is deterministic:

        1. PRICING_QUOTE_ISSUED
        2. PRICING_ADJUSTED
           only when governed adjustments were supplied
        3. FINANCIAL_ALLOCATION_CREATED
           only when a financial allocation exists

    ride_id is required only when a financial allocation
    exists and must be published.
    """

    pricing = orchestrate_pricing(
        request=request,
        quote_id=quote_id,
        calculated_at=calculated_at,
        adjustments=adjustments,
        commission_policy=commission_policy,
        valid_until=valid_until,
    )

    if pricing.financial_allocation is not None:
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
                (
                    "ride_id must be a positive integer "
                    "when the pricing workflow creates "
                    "a financial allocation."
                )
            )

    events: list[
        Event
    ] = []

    quote_event = (
        publish_pricing_quote_issued_event(
            pricing.quote
        )
    )

    events.append(
        quote_event
    )

    if pricing.adjusted_result.applied_adjustments:
        adjustment_event = (
            publish_pricing_adjusted_event(
                pricing_quote_id=(
                    pricing.quote.quote_id
                ),
                request_id=(
                    pricing.request.request_id
                ),
                result=(
                    pricing.adjusted_result
                ),
            )
        )

        events.append(
            adjustment_event
        )

    if pricing.financial_allocation is not None:
        financial_event = (
            publish_financial_allocation_created_event(
                ride_id=ride_id,
                pricing_quote_id=(
                    pricing.quote.quote_id
                ),
                allocation=(
                    pricing.financial_allocation
                ),
            )
        )

        events.append(
            financial_event
        )

    return PricingWorkflowResult(
        pricing=pricing,
        events=tuple(
            events
        ),
    )