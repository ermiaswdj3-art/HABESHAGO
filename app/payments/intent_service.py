"""
HABESHAGO Payment Intent Service

Creates canonical PaymentIntent and PaymentTransaction
objects from validated PaymentRequest contracts.

Commit #94 establishes controlled payment intent creation
and transaction initialization only.

This service does not:
- call payment providers
- contact Telebirr
- contact CBE Birr
- contact Chapa
- contact ArifPay
- confirm payment success
- persist payment records
- publish events
"""

from datetime import (
    datetime,
    timedelta,
)

from app.payments.constants import (
    PaymentIntentStatus,
    PaymentMethod,
    PaymentProvider,
    PaymentTransactionStatus,
)

from app.payments.exceptions import (
    PaymentMethodError,
    PaymentValidationError,
)

from app.payments.models import (
    PaymentIntent,
    PaymentRequest,
    PaymentTransaction,
)


PAYMENT_METHOD_PROVIDER_MAP = {
    PaymentMethod.CASH: (
        PaymentProvider.CASH
    ),
    PaymentMethod.TELEBIRR: (
        PaymentProvider.TELEBIRR
    ),
    PaymentMethod.CBE_BIRR: (
        PaymentProvider.CBE_BIRR
    ),
    PaymentMethod.CHAPA: (
        PaymentProvider.CHAPA
    ),
    PaymentMethod.ARIFPAY: (
        PaymentProvider.ARIFPAY
    ),
    PaymentMethod.AWASH_BANK: (
        PaymentProvider.AWASH_BANK
    ),
    PaymentMethod.AMHARA_BANK: (
        PaymentProvider.AMHARA_BANK
    ),
    PaymentMethod.BANK_OF_ABYSSINIA: (
        PaymentProvider.BANK_OF_ABYSSINIA
    ),
    PaymentMethod.DASHEN_BANK: (
        PaymentProvider.DASHEN_BANK
    ),
}


def _require_aware_datetime(
    value,
    *,
    field_name: str,
) -> datetime:
    """
    Require one explicit timezone-aware timestamp.
    """

    if not isinstance(
        value,
        datetime,
    ):
        raise PaymentValidationError(
            f"{field_name} must be datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PaymentValidationError(
            (
                f"{field_name} must be "
                "timezone-aware."
            )
        )

    return value


def resolve_payment_provider(
    payment_method: str,
) -> str:
    """
    Resolve the canonical provider for one payment method.

    This mapping is deterministic and contains no provider
    execution logic.
    """

    if not isinstance(
        payment_method,
        str,
    ):
        raise PaymentMethodError(
            "payment_method must be str."
        )

    normalized_method = (
        payment_method.strip().lower()
    )

    provider = (
        PAYMENT_METHOD_PROVIDER_MAP.get(
            normalized_method
        )
    )

    if provider is None:
        raise PaymentMethodError(
            (
                "Unsupported payment method: "
                f"{normalized_method}"
            )
        )

    return provider


def create_payment_intent(
    *,
    payment_request: PaymentRequest,
    intent_reference: str,
    created_at: datetime,
    expires_at: datetime | None = None,
) -> PaymentIntent:
    """
    Create one canonical PaymentIntent.

    When expires_at is omitted, the intent receives a
    controlled 15-minute validity window.
    """

    if not isinstance(
        payment_request,
        PaymentRequest,
    ):
        raise PaymentValidationError(
            (
                "payment_request must be a "
                "PaymentRequest."
            )
        )

    created_time = (
        _require_aware_datetime(
            created_at,
            field_name="created_at",
        )
    )

    effective_expiry = (
        expires_at
        if expires_at is not None
        else (
            created_time
            + timedelta(
                minutes=15
            )
        )
    )

    _require_aware_datetime(
        effective_expiry,
        field_name="expires_at",
    )

    provider = resolve_payment_provider(
        payment_request.payment_method
    )

    return PaymentIntent(
        payment_request=payment_request,
        provider=provider,
        intent_reference=intent_reference,
        status=PaymentIntentStatus.CREATED,
        created_at=created_time,
        expires_at=effective_expiry,
    )


def create_payment_transaction(
    *,
    intent: PaymentIntent,
    transaction_reference: str,
    created_at: datetime,
) -> PaymentTransaction:
    """
    Create one canonical PaymentTransaction from an
    existing PaymentIntent.

    The transaction copies the authoritative payment facts
    from the linked obligation and request.

    No provider operation occurs here.
    """

    if not isinstance(
        intent,
        PaymentIntent,
    ):
        raise PaymentValidationError(
            "intent must be a PaymentIntent."
        )

    created_time = (
        _require_aware_datetime(
            created_at,
            field_name="created_at",
        )
    )

    if created_time < intent.created_at:
        raise PaymentValidationError(
            (
                "Transaction created_at cannot be "
                "earlier than PaymentIntent created_at."
            )
        )

    request = intent.payment_request

    obligation = request.obligation

    return PaymentTransaction(
        intent_reference=(
            intent.intent_reference
        ),
        transaction_reference=(
            transaction_reference
        ),
        provider=intent.provider,
        payment_method=(
            request.payment_method
        ),
        amount=obligation.amount,
        currency=obligation.currency,
        status=(
            PaymentTransactionStatus.CREATED
        ),
        payer_id=request.payer_id,
        obligation_reference=(
            obligation.obligation_reference
        ),
        created_at=created_time,
    )