"""
HABESHAGO Ride Commerce Orchestrator

Connects one canonical HABESHAGO ride to an already
authoritative Pricing workflow, Ride Settlement and the
Commerce Platform.

Authority boundaries:

Ride Platform:
- ride_id
- passenger_id
- selected payment_method
- ride lifecycle

Pricing Platform:
- passenger fare
- currency
- financial allocation
- pricing provenance

Ride Settlement Platform:
- authoritative ride financial allocation persistence
- financial completion of the ride

Commerce / Payment Platform:
- payment obligation
- payment request
- payment intent
- payment transaction

This orchestrator does not:
- calculate fares
- calculate commission
- calculate driver earnings
- trust caller-supplied passenger identity
- trust caller-supplied payment method
- execute payment providers
- verify payments
- reconcile payments
"""

from datetime import (
    datetime,
)

from app.commerce import (
    prepare_commerce_payment,
)

from app.pricing.workflow import (
    PricingWorkflowResult,
)

from app.ride_commerce.context_loader import (
    load_ride_commerce_context,
)

from app.ride_commerce.orchestration import (
    RideCommerceOrchestrationResult,
    RideCommerceStatus,
)

from app.services.ride_settlement_service import (
    settle_completed_ride,
)


def _require_positive_integer(
    value: int,
    *,
    field_name: str,
) -> None:
    """
    Require one positive integer identifier.
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
) -> str:
    """
    Require and normalize non-empty text.
    """

    if not isinstance(
        value,
        str,
    ):
        raise ValueError(
            f"{field_name} must be str."
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return normalized


def _require_aware_datetime(
    value,
    *,
    field_name: str,
) -> datetime:
    """
    Require one timezone-aware datetime.
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


def prepare_ride_commerce_payment(
    *,
    ride_id: int,
    pricing_workflow: PricingWorkflowResult,
    obligation_reference: str,
    payment_request_reference: str,
    intent_reference: str,
    transaction_reference: str,
    created_at: datetime,
    expires_at: datetime | None = None,
) -> RideCommerceOrchestrationResult:
    """
    Prepare Commerce Payment for one canonical ride.

    Operational payer and payment method are loaded from
    HABESHAGO's authoritative database.

    Monetary values come exclusively from Pricing.

    Before Commerce preparation, the authoritative
    Pricing FinancialAllocation is attached to the ride
    through the Ride Settlement Platform.

    The caller cannot override:
    - passenger identity;
    - payment method;
    - passenger fare;
    - commission;
    - driver earnings.
    """

    _require_positive_integer(
        ride_id,
        field_name="ride_id",
    )

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

    normalized_obligation_reference = (
        _require_text(
            obligation_reference,
            field_name=(
                "obligation_reference"
            ),
        )
    )

    normalized_payment_request_reference = (
        _require_text(
            payment_request_reference,
            field_name=(
                "payment_request_reference"
            ),
        )
    )

    normalized_intent_reference = (
        _require_text(
            intent_reference,
            field_name="intent_reference",
        )
    )

    normalized_transaction_reference = (
        _require_text(
            transaction_reference,
            field_name=(
                "transaction_reference"
            ),
        )
    )

    commerce_time = (
        _require_aware_datetime(
            created_at,
            field_name="created_at",
        )
    )

    if expires_at is not None:
        payment_expiry = (
            _require_aware_datetime(
                expires_at,
                field_name="expires_at",
            )
        )

        if payment_expiry <= commerce_time:
            raise ValueError(
                (
                    "expires_at must be later "
                    "than created_at."
                )
            )

    else:
        payment_expiry = None

    # ==========================================
    # CANONICAL OPERATIONAL CONTEXT
    # ==========================================

    context = (
        load_ride_commerce_context(
            ride_id
        )
    )

    # ==========================================
    # AUTHORITATIVE PRICING REQUIREMENT
    # ==========================================

    allocation = (
        pricing_workflow
        .pricing
        .financial_allocation
    )

    if allocation is None:
        raise ValueError(
            (
                "Ride Commerce requires an "
                "authoritative Pricing financial "
                "allocation."
            )
        )

    # ==========================================
    # RIDE SETTLEMENT PLATFORM
    # ==========================================
    #
    # Attach the exact Pricing allocation to the
    # canonical ride.
    #
    # The Ride Settlement Platform owns this
    # persistence responsibility.
    #
    # No financial recalculation occurs here.
    # ==========================================

    settle_completed_ride(
        context.ride_id,
        financial_allocation=allocation,
    )

    # ==========================================
    # COMMERCE PLATFORM
    # ==========================================

    commerce_result = (
        prepare_commerce_payment(
            pricing_workflow=(
                pricing_workflow
            ),
            obligation_reference=(
                normalized_obligation_reference
            ),
            source_type="ride",
            source_reference=str(
                context.ride_id
            ),
            payer_id=(
                context.passenger_id
            ),
            payment_method=(
                context.payment_method
            ),
            payment_request_reference=(
                normalized_payment_request_reference
            ),
            intent_reference=(
                normalized_intent_reference
            ),
            transaction_reference=(
                normalized_transaction_reference
            ),
            created_at=commerce_time,
            expires_at=payment_expiry,
        )
    )

    # ==========================================
    # RIDE COMMERCE RESULT
    # ==========================================

    return RideCommerceOrchestrationResult(
        context=context,
        pricing_workflow=pricing_workflow,
        commerce_result=commerce_result,
        status=(
            RideCommerceStatus.PAYMENT_PREPARED
        ),
    )