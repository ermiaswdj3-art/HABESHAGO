"""
HABESHAGO Commerce Orchestrator

Coordinates the production boundary between an already
completed authoritative Pricing workflow and Payment
workflow preparation.

Flow:

    PricingWorkflowResult
            ↓
    PaymentObligation
            ↓
    PaymentRequest
            ↓
    Payment Intent
            ↓
    Payment Transaction
            ↓
    CommerceOrchestrationResult

Pricing remains authoritative for money.

Payment remains authoritative for payment processing.
"""

from datetime import (
    datetime,
)

from app.commerce.orchestration import (
    CommerceOrchestrationResult,
    CommerceWorkflowStatus,
)

from app.commerce.pricing_payment_bridge import (
    build_payment_obligation_from_pricing,
)

from app.payments.models import (
    PaymentRequest,
)

from app.payments.orchestrator import (
    prepare_payment,
)

from app.pricing.workflow import (
    PricingWorkflowResult,
)


def _require_aware_datetime(
    value,
    *,
    field_name: str,
) -> datetime:
    """
    Require one explicit timezone-aware Commerce time.
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


def prepare_commerce_payment(
    *,
    pricing_workflow: PricingWorkflowResult,
    obligation_reference: str,
    source_type: str,
    source_reference: str,
    payer_id: int,
    payment_method: str,
    payment_request_reference: str,
    intent_reference: str,
    transaction_reference: str,
    created_at: datetime,
    expires_at: datetime | None = None,
) -> CommerceOrchestrationResult:
    """
    Prepare Payment from one completed authoritative
    Pricing workflow.

    No monetary amount is supplied by the caller.

    The Payment obligation amount comes exclusively from
    Pricing's FinancialAllocation.passenger_fare.

    created_at is deliberately explicit and shared across
    the Commerce-created Payment records so retries remain
    deterministic.
    """

    if not isinstance(
        pricing_workflow,
        PricingWorkflowResult,
    ):
        raise ValueError(
            (
                "pricing_workflow must be a "
                "PricingWorkflowResult."
            )
        )

    commerce_time = (
        _require_aware_datetime(
            created_at,
            field_name="created_at",
        )
    )

    pricing = pricing_workflow.pricing

    # ==========================================
    # PRICING → PAYMENT BRIDGE
    # ==========================================

    obligation = (
        build_payment_obligation_from_pricing(
            pricing_result=pricing,
            obligation_reference=(
                obligation_reference
            ),
            source_type=source_type,
            source_reference=(
                source_reference
            ),
            created_at=commerce_time,
        )
    )

    # ==========================================
    # PAYMENT REQUEST
    # ==========================================

    payment_request = PaymentRequest(
        obligation=obligation,
        payer_id=payer_id,
        payment_method=payment_method,
        request_reference=(
            payment_request_reference
        ),
        requested_at=commerce_time,
    )

    # ==========================================
    # PAYMENT PLATFORM
    # ==========================================

    payment_workflow = prepare_payment(
        obligation=obligation,
        payment_request=payment_request,
        intent_reference=intent_reference,
        transaction_reference=(
            transaction_reference
        ),
        created_at=commerce_time,
        expires_at=expires_at,
    )

    # ==========================================
    # COMMERCE RESULT
    # ==========================================

    return CommerceOrchestrationResult(
        pricing_workflow=pricing_workflow,
        payment_obligation=obligation,
        payment_workflow=payment_workflow,
        status=(
            CommerceWorkflowStatus.PAYMENT_PREPARED
        ),
    )