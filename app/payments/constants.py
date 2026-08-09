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
    """

    CASH = "cash"

    TELEBIRR = "telebirr"

    CBE_BIRR = "cbe_birr"

    CHAPA = "chapa"

    ARIFPAY = "arifpay"

    ALL = {
        CASH,
        TELEBIRR,
        CBE_BIRR,
        CHAPA,
        ARIFPAY,
    }


class PaymentProvider:
    """
    Canonical payment-processing authority.

    Cash is represented explicitly because it has a
    different verification lifecycle from digital
    providers.
    """

    CASH = "cash"

    TELEBIRR = "telebirr"

    CBE_BIRR = "cbe_birr"

    CHAPA = "chapa"

    ARIFPAY = "arifpay"

    ALL = {
        CASH,
        TELEBIRR,
        CBE_BIRR,
        CHAPA,
        ARIFPAY,
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