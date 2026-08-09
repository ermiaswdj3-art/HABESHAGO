"""
HABESHAGO Payment Platform Constants

Defines the canonical vocabulary shared across the
HABESHAGO Payment Platform.

These constants describe payment concepts only.

They do not:
- process payments
- call providers
- move money
- confirm payment success
- persist transactions
"""


class PaymentCurrency:
    """
    Supported payment currencies.
    """

    ETB = "ETB"

    ALL = {
        ETB,
    }


class PaymentMethod:
    """
    Canonical passenger payment methods.

    A payment method describes how the payer chooses to
    fulfill a payment obligation.

    Provider execution is handled separately by the
    Payment Provider Gateway.
    """

    CASH = "cash"

    TELEBIRR = "telebirr"

    CBE_BIRR = "cbe_birr"

    CHAPA = "chapa"

    ARIFPAY = "arifpay"

    AWASH_BANK = "awash_bank"

    AMHARA_BANK = "amhara_bank"

    BANK_OF_ABYSSINIA = (
        "bank_of_abyssinia"
    )

    DASHEN_BANK = "dashen_bank"

    ALL = {
        CASH,
        TELEBIRR,
        CBE_BIRR,
        CHAPA,
        ARIFPAY,
        AWASH_BANK,
        AMHARA_BANK,
        BANK_OF_ABYSSINIA,
        DASHEN_BANK,
    }


class PaymentProvider:
    """
    Canonical payment-processing authorities.

    Provider identity is intentionally separate from
    PaymentMethod so future payment rails can evolve
    without changing the payment-domain contract.
    """

    CASH = "cash"

    TELEBIRR = "telebirr"

    CBE_BIRR = "cbe_birr"

    CHAPA = "chapa"

    ARIFPAY = "arifpay"

    AWASH_BANK = "awash_bank"

    AMHARA_BANK = "amhara_bank"

    BANK_OF_ABYSSINIA = (
        "bank_of_abyssinia"
    )

    DASHEN_BANK = "dashen_bank"

    ALL = {
        CASH,
        TELEBIRR,
        CBE_BIRR,
        CHAPA,
        ARIFPAY,
        AWASH_BANK,
        AMHARA_BANK,
        BANK_OF_ABYSSINIA,
        DASHEN_BANK,
    }


class PaymentStatus:
    """
    Canonical high-level Payment Platform lifecycle.

    Commit #93 defines vocabulary only.

    Lifecycle behavior will be implemented by later
    payment commits.
    """

    CREATED = "created"

    METHOD_SELECTED = "method_selected"

    PENDING = "pending"

    PROCESSING = "processing"

    AUTHORIZED = "authorized"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    EXPIRED = "expired"

    REFUNDED = "refunded"

    ALL = {
        CREATED,
        METHOD_SELECTED,
        PENDING,
        PROCESSING,
        AUTHORIZED,
        COMPLETED,
        FAILED,
        CANCELLED,
        EXPIRED,
        REFUNDED,
    }


class PaymentSource:
    """
    Canonical source of the financial obligation.
    """

    RIDE = "ride"

    DELIVERY = "delivery"

    OTHER = "other"

    ALL = {
        RIDE,
        DELIVERY,
        OTHER,
    }


class PaymentIntentStatus:
    """
    Canonical lifecycle for one Payment Intent.
    """

    CREATED = "created"

    READY = "ready"

    SUBMITTED = "submitted"

    CANCELLED = "cancelled"

    EXPIRED = "expired"

    COMPLETED = "completed"

    ALL = {
        CREATED,
        READY,
        SUBMITTED,
        CANCELLED,
        EXPIRED,
        COMPLETED,
    }


class PaymentTransactionStatus:
    """
    Canonical lifecycle for one payment transaction.
    """

    CREATED = "created"

    PENDING = "pending"

    PROCESSING = "processing"

    AUTHORIZED = "authorized"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    EXPIRED = "expired"

    REFUNDED = "refunded"

    ALL = {
        CREATED,
        PENDING,
        PROCESSING,
        AUTHORIZED,
        COMPLETED,
        FAILED,
        CANCELLED,
        EXPIRED,
        REFUNDED,
    }