"""
HABESHAGO Payment Platform Exceptions

Defines the canonical exception hierarchy used by the
shared Payment Platform.
"""


class PaymentError(Exception):
    """
    Base exception for Payment Platform failures.
    """


class PaymentValidationError(
    PaymentError
):
    """
    Raised when a payment-domain contract is invalid.
    """


class PaymentMethodError(
    PaymentError
):
    """
    Raised when a payment method is unsupported or invalid.
    """


class PaymentProviderError(
    PaymentError
):
    """
    Raised for payment-provider processing failures.
    """


class PaymentStateError(
    PaymentError
):
    """
    Raised when a payment lifecycle transition is invalid.
    """


class PaymentPersistenceError(
    PaymentError
):
    """
    Raised when durable payment persistence fails.
    """


class PaymentReconciliationError(
    PaymentError
):
    """
    Raised when financial reconciliation cannot be proven.
    """