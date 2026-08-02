"""
HABESHAGO Pickup Verification Service

Generates and verifies the passenger pickup PIN used
before a ride can begin.
"""

from datetime import datetime, timezone
from secrets import randbelow

from app.mini_app.models import Trip


def generate_pickup_pin(
    trip: Trip,
) -> str:
    """
    Generate and store a secure four-digit pickup PIN.
    """

    if trip.booking_status != "driver_arrived":
        raise ValueError(
            "A pickup PIN can be generated only after "
            "the driver has arrived."
        )

    pickup_pin = f"{randbelow(10000):04d}"

    trip.pickup_pin = pickup_pin
    trip.pickup_pin_generated_at = datetime.now(
        timezone.utc
    ).isoformat()
    trip.pickup_pin_verified = False
    trip.pickup_verified_at = None
    trip.pickup_verification_attempts = 0

    trip.set_booking_status(
        "pickup_verification_pending"
    )

    return pickup_pin


def verify_pickup_pin(
    trip: Trip,
    submitted_pin: str,
) -> bool:
    """
    Verify a passenger-provided pickup PIN.
    """

    if not trip.is_ready_for_pickup_verification():
        raise ValueError(
            "The trip is not ready for pickup verification."
        )

    clean_pin = str(submitted_pin or "").strip()

    trip.pickup_verification_attempts += 1

    if clean_pin != trip.pickup_pin:
        return False

    trip.pickup_pin_verified = True
    trip.pickup_verified_at = datetime.now(
        timezone.utc
    ).isoformat()

    trip.set_booking_status("passenger_verified")
    trip.set_booking_status("ready_to_start")

    return True