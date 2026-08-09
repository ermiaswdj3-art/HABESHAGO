"""
HABESHAGO Payment Platform Contracts

Defines interfaces expected from later Payment Platform
components.

Commit #93 established the foundational payment contracts.

Commit #94 extends those contracts with canonical
PaymentIntent and PaymentTransaction lifecycle objects.

Provider execution and persistence implementations arrive
in later payment commits.
"""

from datetime import (
    datetime,
)

from typing import (
    Protocol,
)

from app.payments.provider import (
    PaymentExecutionRequest,
    PaymentExecutionResult,
)

from app.payments.models import (
    PaymentIntent,
    PaymentObligation,
    PaymentRequest,
    PaymentTransaction,
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


class PaymentIntentRepository(
    Protocol
):
    """
    Contract for durable PaymentIntent persistence.
    """

    def save_intent(
        self,
        intent: PaymentIntent,
    ) -> PaymentIntent:
        ...

    def get_intent(
        self,
        intent_reference: str,
    ) -> PaymentIntent | None:
        ...


class PaymentTransactionRepository(
    Protocol
):
    """
    Contract for durable PaymentTransaction persistence.
    """

    def save_transaction(
        self,
        transaction: PaymentTransaction,
    ) -> PaymentTransaction:
        ...

    def get_transaction(
        self,
        transaction_reference: str,
    ) -> PaymentTransaction | None:
        ...


class PaymentProviderGateway(
    Protocol
):
    """
    Contract implemented by payment-provider adapters.

    A provider adapter must:
    - identify itself canonically;
    - declare supported payment methods;
    - execute one provider-independent request;
    - return one canonical execution result.
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

    def execute(
        self,
        request: PaymentExecutionRequest,
        *,
        processed_at: datetime,
    ) -> PaymentExecutionResult:
        ...


class PaymentPlatformContract(
    Protocol
):
    """
    High-level contract for the shared HABESHAGO Payment
    Platform.

    Commit #94 defines lifecycle creation only.

    Provider execution remains a later responsibility.
    """

    def create_payment_request(
        self,
        *,
        obligation: PaymentObligation,
        payer_id: int,
        payment_method: str,
    ) -> PaymentRequest:
        ...

    def create_payment_intent(
        self,
        *,
        payment_request: PaymentRequest,
        intent_reference: str,
        created_at: datetime,
        expires_at: datetime | None = None,
    ) -> PaymentIntent:
        ...

    def create_payment_transaction(
        self,
        *,
        intent: PaymentIntent,
        transaction_reference: str,
        created_at: datetime,
    ) -> PaymentTransaction:
        ...