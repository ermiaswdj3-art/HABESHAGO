"""
HABESHAGO Payment Provider Adapters

Defines provider-specific execution adapters behind the
shared Payment Provider Gateway boundary.

Commit #96 includes:
- one controlled Cash adapter;
- safe unavailable adapters for digital providers.

Digital adapters deliberately do not call real external
APIs yet.
"""

from datetime import (
    datetime,
)

from app.payments.constants import (
    PaymentMethod,
    PaymentProvider,
)

from app.payments.exceptions import (
    PaymentProviderError,
    PaymentValidationError,
)

from app.payments.provider import (
    PaymentExecutionRequest,
    PaymentExecutionResult,
    PaymentExecutionStatus,
)


def _require_execution_request(
    request,
) -> PaymentExecutionRequest:
    """
    Require one canonical PaymentExecutionRequest.
    """

    if not isinstance(
        request,
        PaymentExecutionRequest,
    ):
        raise PaymentValidationError(
            (
                "request must be a "
                "PaymentExecutionRequest."
            )
        )

    return request


def _require_processed_at(
    processed_at,
) -> datetime:
    """
    Require one timezone-aware execution timestamp.
    """

    if not isinstance(
        processed_at,
        datetime,
    ):
        raise PaymentValidationError(
            "processed_at must be datetime."
        )

    if (
        processed_at.tzinfo is None
        or processed_at.utcoffset() is None
    ):
        raise PaymentValidationError(
            (
                "processed_at must be "
                "timezone-aware."
            )
        )

    return processed_at


class CashPaymentAdapter:
    """
    Controlled adapter for cash payment selection.

    Cash selection is not treated as verified digital
    settlement.

    The adapter therefore returns PENDING so later
    verification can confirm that cash was actually
    received.
    """

    def provider_name(
        self,
    ) -> str:
        return PaymentProvider.CASH

    def supports_payment_method(
        self,
        payment_method: str,
    ) -> bool:
        return (
            payment_method
            == PaymentMethod.CASH
        )

    def execute(
        self,
        request: PaymentExecutionRequest,
        *,
        processed_at: datetime,
    ) -> PaymentExecutionResult:
        _require_execution_request(
            request
        )

        _require_processed_at(
            processed_at
        )

        if (
            request.provider
            != PaymentProvider.CASH
        ):
            raise PaymentProviderError(
                (
                    "Cash adapter cannot execute "
                    "another provider's request."
                )
            )

        return PaymentExecutionResult(
            transaction_reference=(
                request.transaction_reference
            ),
            provider=PaymentProvider.CASH,
            status=(
                PaymentExecutionStatus.PENDING
            ),
            processed_at=processed_at,
        )


class UnavailablePaymentAdapter:
    """
    Safe adapter placeholder for a provider whose real
    production integration is not configured yet.

    This adapter never simulates success.
    """

    def __init__(
        self,
        *,
        provider: str,
        payment_method: str,
    ) -> None:
        if provider not in PaymentProvider.ALL:
            raise PaymentValidationError(
                (
                    "Unsupported provider: "
                    f"{provider}"
                )
            )

        if payment_method not in PaymentMethod.ALL:
            raise PaymentValidationError(
                (
                    "Unsupported payment method: "
                    f"{payment_method}"
                )
            )

        self._provider = provider
        self._payment_method = (
            payment_method
        )

    def provider_name(
        self,
    ) -> str:
        return self._provider

    def supports_payment_method(
        self,
        payment_method: str,
    ) -> bool:
        return (
            payment_method
            == self._payment_method
        )

    def execute(
        self,
        request: PaymentExecutionRequest,
        *,
        processed_at: datetime,
    ) -> PaymentExecutionResult:
        _require_execution_request(
            request
        )

        _require_processed_at(
            processed_at
        )

        if (
            request.provider
            != self._provider
        ):
            raise PaymentProviderError(
                (
                    "Payment adapter provider "
                    "does not match execution request."
                )
            )

        raise PaymentProviderError(
            (
                "Payment provider is not configured "
                "for real execution: "
                f"{self._provider}"
            )
        )