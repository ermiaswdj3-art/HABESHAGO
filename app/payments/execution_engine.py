"""
HABESHAGO Payment Execution Engine

Coordinates provider execution for one canonical
PaymentTransaction.

Commit #96 keeps provider-specific behavior behind the
Payment Provider Gateway and Provider Registry.

The engine:
- validates the authoritative PaymentTransaction;
- creates a provider-independent execution request;
- resolves the registered provider adapter;
- executes through that adapter;
- validates the returned execution result.

The engine does not:
- modify authoritative pricing;
- persist transaction state;
- reconcile provider money;
- publish events;
- depend on Telegram or the Mini App.
"""

from datetime import (
    datetime,
)

from app.payments.exceptions import (
    PaymentProviderError,
    PaymentValidationError,
)

from app.payments.models import (
    PaymentTransaction,
)

from app.payments.provider import (
    PaymentExecutionRequest,
    PaymentExecutionResult,
)

from app.payments.provider_registry import (
    get_payment_provider_adapter,
)


def _require_aware_datetime(
    value,
    *,
    field_name: str,
) -> datetime:
    """
    Require one explicit timezone-aware execution time.
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


def build_payment_execution_request(
    *,
    transaction: PaymentTransaction,
    requested_at: datetime,
) -> PaymentExecutionRequest:
    """
    Build one canonical provider-independent execution
    request from an authoritative PaymentTransaction.
    """

    if not isinstance(
        transaction,
        PaymentTransaction,
    ):
        raise PaymentValidationError(
            (
                "transaction must be a "
                "PaymentTransaction."
            )
        )

    execution_time = (
        _require_aware_datetime(
            requested_at,
            field_name="requested_at",
        )
    )

    if (
        execution_time
        < transaction.created_at
    ):
        raise PaymentValidationError(
            (
                "requested_at cannot be earlier "
                "than PaymentTransaction created_at."
            )
        )

    return PaymentExecutionRequest(
        transaction_reference=(
            transaction.transaction_reference
        ),
        provider=transaction.provider,
        amount=transaction.amount,
        currency=transaction.currency,
        payer_id=transaction.payer_id,
        obligation_reference=(
            transaction.obligation_reference
        ),
        requested_at=execution_time,
    )


def execute_payment_transaction(
    *,
    transaction: PaymentTransaction,
    processed_at: datetime,
) -> PaymentExecutionResult:
    """
    Execute one authoritative PaymentTransaction through
    the registered provider adapter.

    The adapter result must preserve:
    - transaction reference;
    - provider identity.

    No persistence occurs in this engine.
    """

    execution_time = (
        _require_aware_datetime(
            processed_at,
            field_name="processed_at",
        )
    )

    request = (
        build_payment_execution_request(
            transaction=transaction,
            requested_at=execution_time,
        )
    )

    adapter = (
        get_payment_provider_adapter(
            transaction.provider
        )
    )

    if not adapter.supports_payment_method(
        transaction.payment_method
    ):
        raise PaymentProviderError(
            (
                "Registered payment adapter does "
                "not support the transaction's "
                "payment method."
            )
        )

    result = adapter.execute(
        request,
        processed_at=execution_time,
    )

    if not isinstance(
        result,
        PaymentExecutionResult,
    ):
        raise PaymentProviderError(
            (
                "Payment provider adapter returned "
                "an invalid execution result."
            )
        )

    if (
        result.transaction_reference
        != transaction.transaction_reference
    ):
        raise PaymentProviderError(
            (
                "Payment execution result transaction "
                "reference does not match the "
                "authoritative transaction."
            )
        )

    if (
        result.provider
        != transaction.provider
    ):
        raise PaymentProviderError(
            (
                "Payment execution result provider "
                "does not match the authoritative "
                "transaction."
            )
        )

    return result