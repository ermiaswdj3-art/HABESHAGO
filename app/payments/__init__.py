"""
HABESHAGO Payment Platform

Canonical domain contracts for authoritative,
versioned and auditable payment processing.

Commit #93 establishes Payment Platform language and
contracts only.

No real payment processing occurs in this package yet.
"""

from app.payments.constants import (
    PaymentCurrency,
    PaymentMethod,
    PaymentProvider,
    PaymentSource,
    PaymentStatus,
)

from app.payments.contracts import (
    PaymentObligationRepository,
    PaymentPlatformContract,
    PaymentProviderGateway,
    PaymentRequestRepository,
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

from app.payments.models import (
    PaymentObligation,
    PaymentRequest,
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
    "PaymentValidationError",
]