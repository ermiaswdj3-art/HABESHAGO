"""
HABESHAGO Pricing → Payment Bridge

Connects an authoritative Pricing Platform result
to the canonical Payment Platform obligation.

Financial authority remains with Pricing.

Responsibilities:
- Require an authoritative Pricing orchestration result
- Require a completed financial allocation
- Preserve the exact passenger fare
- Preserve the exact pricing currency
- Preserve Pricing request and quote provenance
- Preserve an explicit deterministic creation time
- Create the canonical PaymentObligation

This bridge does not:
- calculate fares
- apply pricing adjustments
- calculate commission
- calculate driver earnings
- modify pricing results
- execute payments
- select payment providers
- verify payments
- reconcile payments
- perform settlement
"""

from datetime import (
    datetime,
)

from app.payments.models import (
    PaymentObligation,
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
    Require one explicit timezone-aware datetime.
    """

    if not isinstance(
        value,
        datetime,
    ):
        raise ValueError(
            f"{field_name} must be datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            (
                f"{field_name} must be "
                "timezone-aware."
            )
        )

    return value


def build_payment_obligation_from_pricing(
    *,
    pricing_result: PricingOrchestrationResult,
    obligation_reference: str,
    source_type: str,
    source_reference: str,
    created_at: datetime,
) -> PaymentObligation:
    """
    Convert one authoritative Pricing result into one
    canonical Payment obligation.

    The exact passenger fare produced by Pricing becomes
    the amount owed by the payer.

    created_at is explicitly supplied so retries of the
    same Commerce operation construct the same immutable
    Payment obligation.

    No financial value is recalculated here.
    """

    if not isinstance(
        pricing_result,
        PricingOrchestrationResult,
    ):
        raise ValueError(
            (
                "pricing_result must be a "
                "PricingOrchestrationResult."
            )
        )

    allocation = (
        pricing_result.financial_allocation
    )

    if allocation is None:
        raise ValueError(
            (
                "Pricing result must contain a "
                "financial allocation before a "
                "Payment obligation can be created."
            )
        )

    normalized_obligation_reference = str(
        obligation_reference or ""
    ).strip()

    if not normalized_obligation_reference:
        raise ValueError(
            "obligation_reference cannot be empty."
        )

    normalized_source_type = str(
        source_type or ""
    ).strip()

    if not normalized_source_type:
        raise ValueError(
            "source_type cannot be empty."
        )

    normalized_source_reference = str(
        source_reference or ""
    ).strip()

    if not normalized_source_reference:
        raise ValueError(
            "source_reference cannot be empty."
        )

    obligation_created_at = (
        _require_aware_datetime(
            created_at,
            field_name="created_at",
        )
    )

    return PaymentObligation(
        obligation_reference=(
            normalized_obligation_reference
        ),
        source_type=normalized_source_type,
        source_reference=(
            normalized_source_reference
        ),
        amount=allocation.passenger_fare,
        currency=allocation.currency,
        pricing_quote_id=(
            pricing_result.quote.quote_id
        ),
        pricing_request_id=(
            pricing_result.request.request_id
        ),
        created_at=obligation_created_at,
    )