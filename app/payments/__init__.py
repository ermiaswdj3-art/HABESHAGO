"""
HABESHAGO Payment Platform

Canonical domain contracts for authoritative,
versioned and auditable payment processing.

Commit #93 established Payment Platform language and
contracts.

Commit #94 adds canonical PaymentIntent and
PaymentTransaction lifecycle creation.

No real payment-provider execution occurs in this package
yet.
"""

from app.payments.constants import (
    PaymentCurrency,
    PaymentIntentStatus,
    PaymentMethod,
    PaymentProvider,
    PaymentSource,
    PaymentStatus,
    PaymentTransactionStatus,
)

from app.payments.contracts import (
    PaymentIntentRepository,
    PaymentObligationRepository,
    PaymentPlatformContract,
    PaymentProviderGateway,
    PaymentRequestRepository,
    PaymentTransactionRepository,
)

from app.payments.exceptions import (
    PaymentError,
    PaymentMethodError,
    PaymentPersistenceError,
    PaymentProviderError,
    PaymentReconciliationError,
    PaymentStateError,
    PaymentValidationError,
)

from app.payments.intent_service import (
    create_payment_intent,
    create_payment_transaction,
    resolve_payment_provider,
)

from app.payments.models import (
    PaymentIntent,
    PaymentObligation,
    PaymentRequest,
    PaymentTransaction,
)

from app.payments.execution_engine import (
    build_payment_execution_request,
    execute_payment_transaction,
)

from app.payments.provider import (
    PaymentExecutionRequest,
    PaymentExecutionResult,
    PaymentExecutionStatus,
)

from app.payments.reconciliation import (
    PaymentReconciliationResult,
    PaymentReconciliationStatus,
    reconcile_payment,
)

from app.payments.verification import (
    PaymentVerificationResult,
    PaymentVerificationStatus,
    ProviderPaymentStatus,
    ProviderVerificationEvidence,
    verify_payment_evidence,
)

from app.payments.provider_adapters import (
    CashPaymentAdapter,
    UnavailablePaymentAdapter,
)

from app.payments.provider_registry import (
    get_payment_provider_adapter,
    list_registered_payment_providers,
)

from app.payments.versions import (
    PAYMENT_CONTRACT_VERSION,
    PAYMENT_PLATFORM_VERSION,
)


__all__ = [
    "PAYMENT_CONTRACT_VERSION",
    "PAYMENT_PLATFORM_VERSION",
    "PaymentCurrency",
    "PaymentError",
    "PaymentIntent",
    "PaymentIntentRepository",
    "PaymentIntentStatus",
    "PaymentMethod",
    "PaymentMethodError",
    "PaymentObligation",
    "PaymentObligationRepository",
    "PaymentPersistenceError",
    "PaymentPlatformContract",
    "PaymentProvider",
    "PaymentProviderError",
    "PaymentProviderGateway",
    "PaymentReconciliationError",
    "PaymentRequest",
    "PaymentRequestRepository",
    "PaymentSource",
    "PaymentStateError",
    "PaymentStatus",
    "PaymentTransaction",
    "PaymentTransactionRepository",
    "PaymentTransactionStatus",
    "PaymentValidationError",
    "create_payment_intent",
    "create_payment_transaction",
    "CashPaymentAdapter",
    "PaymentExecutionRequest",
    "PaymentExecutionResult",
    "PaymentExecutionStatus",
    "UnavailablePaymentAdapter",
    "build_payment_execution_request",
    "execute_payment_transaction",
    "get_payment_provider_adapter",
    "list_registered_payment_providers",
    "PaymentReconciliationResult",
    "PaymentReconciliationStatus",
    "PaymentVerificationResult",
    "PaymentVerificationStatus",
    "ProviderPaymentStatus",
    "ProviderVerificationEvidence",
    "reconcile_payment",
    "verify_payment_evidence",
    "resolve_payment_provider",
]