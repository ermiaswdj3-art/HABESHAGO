"""
HABESHAGO Payment Platform Contracts

Defines interfaces expected from later Payment Platform
components.

Commit #93 establishes contracts only.

Implementations arrive in later payment commits.
"""

from typing import (
    Protocol,
)

from app.payments.models import (
    PaymentObligation,
    PaymentRequest,
)


class PaymentObligationRepository(
    Protocol
):
    """
    Contract for durable PaymentObligation persistence.
    """

    def save_obligation(
        self,
        obligation: PaymentObligation,
    ) -> PaymentObligation:
        ...

    def get_obligation(
        self,
        obligation_reference: str,
    ) -> PaymentObligation | None:
        ...


class PaymentRequestRepository(
    Protocol
):
    """
    Contract for durable PaymentRequest persistence.
    """

    def save_request(
        self,
        request: PaymentRequest,
    ) -> PaymentRequest:
        ...

    def get_request(
        self,
        request_reference: str,
    ) -> PaymentRequest | None:
        ...


class PaymentProviderGateway(
    Protocol
):
    """
    Contract implemented by future payment-provider
    adapters.

    Examples may eventually include:
    - Telebirr
    - CBE Birr
    - Chapa
    - ArifPay
    - controlled cash verification

    Commit #93 deliberately defines no provider-specific
    request or response implementation.
    """

    def provider_name(
        self,
    ) -> str:
        ...

    def supports_payment_method(
        self,
        payment_method: str,
    ) -> bool:
        ...


class PaymentPlatformContract(
    Protocol
):
    """
    High-level contract for the future shared HABESHAGO
    Payment Platform.

    The concrete lifecycle implementation is intentionally
    deferred to later commits.
    """

    def create_payment_request(
        self,
        *,
        obligation: PaymentObligation,
        payer_id: int,
        payment_method: str,
    ) -> PaymentRequest:
        ...