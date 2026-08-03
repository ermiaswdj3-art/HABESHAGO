"""
HABESHAGO Payment Service

Manages payment method selection, simulated payment
processing, transaction identifiers, and payment completion.

Real provider integrations such as Telebirr, CBE Birr,
Chapa, and ArifPay will later plug into this service.
"""

from datetime import datetime, timezone
from secrets import token_hex

from app.mini_app.models import Trip


SUPPORTED_PAYMENT_METHODS = {
    "cash",
    "telebirr",
    "cbe_birr",
    "chapa",
    "arifpay",
}


def select_payment_method(
    trip: Trip,
    payment_method: str,
) -> Trip:
    """
    Store the passenger's selected payment method.
    """

    if not trip.is_ready_for_payment():
        raise ValueError(
            "The trip is not ready for payment."
        )

    clean_method = str(
        payment_method or ""
    ).strip().lower()

    if clean_method not in SUPPORTED_PAYMENT_METHODS:
        raise ValueError(
            "Unsupported payment method."
        )

    trip.payment_method = clean_method
    trip.set_payment_status(
        "payment_method_selected"
    )

    return trip


def process_payment(
    trip: Trip,
) -> Trip:
    """
    Simulate payment processing for the selected method.

    Cash is recorded as completed for this foundation.
    Digital providers are also simulated as successful.
    """

    if trip.payment_status != "payment_method_selected":
        raise ValueError(
            "Select a payment method before processing."
        )

    if not trip.payment_method:
        raise ValueError(
            "No payment method has been selected."
        )

    trip.set_payment_status(
        "payment_processing"
    )

    transaction_prefix = (
        trip.payment_method.upper()
        .replace("_", "")
    )

    trip.payment_transaction_id = (
        f"{transaction_prefix}-"
        f"{token_hex(5).upper()}"
    )

    trip.payment_completed_at = datetime.now(
        timezone.utc
    ).isoformat()

    trip.receipt_id = (
        f"RCT-{token_hex(5).upper()}"
    )

    trip.set_payment_status(
        "payment_completed"
    )

    return trip