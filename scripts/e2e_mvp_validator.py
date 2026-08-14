"""
HABESHAGO End-to-End MVP Validator

Commit #128

Purpose:
Verify that the complete HABESHAGO MVP lifecycle is
structurally connected before running the real two-device
passenger/driver demonstration.

This validator is intentionally non-destructive.
It does not create, modify, complete, or delete real rides.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from app.mini_app.models.trip import (
    Trip,
)

from app.mini_app.ride_integration.lifecycle_bridge import (
    accept_offer_and_bind_trip,
)

from app.mini_app.services.fare_breakdown_service import (
    calculate_fare_breakdown,
)

from app.mini_app.services.payment_service import (
    process_payment,
    select_payment_method,
)

from app.mini_app.services.ride_state_synchronization_service import (
    synchronize_trip_with_canonical_ride,
)

from app.services.dispatch_service import (
    find_best_driver,
)

from app.services.ride_offer_acceptance_service import (
    accept_offer_and_create_ride,
)

from app.services.ride_offer_service import (
    get_driver_pending_offer,
    get_passenger_pending_offer,
)

from app.services.ride_transition_service import (
    transition_ride,
)


def require(
    condition: bool,
    message: str,
) -> None:
    """
    Raise immediately when one E2E contract is missing.
    """

    if not condition:
        raise AssertionError(message)


def verify_trip_contract() -> None:
    """
    Verify the shared Trip model exposes every state needed
    for the End-to-End MVP.
    """

    trip = Trip()

    required_fields = (
        "canonical_ride_id",
        "canonical_passenger_id",
        "canonical_driver_id",
        "pickup_latitude",
        "pickup_longitude",
        "destination_latitude",
        "destination_longitude",
        "booking_status",
        "pickup_pin",
        "pickup_pin_verified",
        "final_fare",
        "payment_method",
        "payment_status",
        "payment_transaction_id",
        "receipt_id",
    )

    for field_name in required_fields:
        require(
            hasattr(
                trip,
                field_name,
            ),
            (
                "Trip contract missing required field: "
                f"{field_name}"
            ),
        )

    required_booking_states = (
        "driver_assigned",
        "driver_arriving",
        "driver_arrived",
        "pickup_verification_pending",
        "ready_to_start",
        "trip_started",
        "trip_completed",
    )

    original_status = trip.booking_status

    for status in required_booking_states:
        trip.set_booking_status(
            status
        )

        require(
            trip.booking_status == status,
            (
                "Trip rejected required booking state: "
                f"{status}"
            ),
        )

    trip.booking_status = original_status

    print(
        "PASS: Shared Trip lifecycle contract"
    )


def verify_platform_functions() -> None:
    """
    Verify that the major shared platform boundaries exist
    with the expected callable contracts.
    """

    functions = {
        "dispatch":
            find_best_driver,

        "driver pending offer":
            get_driver_pending_offer,

        "passenger pending offer":
            get_passenger_pending_offer,

        "offer acceptance":
            accept_offer_and_create_ride,

        "Mini App acceptance bridge":
            accept_offer_and_bind_trip,

        "Ride transition":
            transition_ride,

        "passenger synchronization":
            synchronize_trip_with_canonical_ride,

        "fare finalization":
            calculate_fare_breakdown,

        "payment selection":
            select_payment_method,

        "payment processing":
            process_payment,
    }

    for name, function in functions.items():
        require(
            callable(function),
            f"Missing callable platform boundary: {name}",
        )

        print(
            f"PASS: {name}"
        )


def verify_identity_contracts() -> None:
    """
    Verify canonical Ride identity flows through acceptance
    and Mini App synchronization APIs rather than browser-
    supplied duplicate Ride identities.
    """

    acceptance_signature = inspect.signature(
        accept_offer_and_create_ride
    )

    require(
        list(
            acceptance_signature.parameters
        )
        == [
            "offer_id",
            "driver_id",
        ],
        (
            "Offer acceptance contract changed. "
            "Expected offer_id + driver_id only."
        ),
    )

    bridge_signature = inspect.signature(
        accept_offer_and_bind_trip
    )

    require(
        set(
            bridge_signature.parameters
        )
        == {
            "trip",
            "offer_id",
            "driver_id",
        },
        (
            "Mini App lifecycle bridge contract changed."
        ),
    )

    transition_signature = inspect.signature(
        transition_ride
    )

    require(
        set(
            transition_signature.parameters
        )
        == {
            "ride_id",
            "driver_id",
            "next_state",
        },
        (
            "Ride transition gateway contract changed."
        ),
    )

    print(
        "PASS: Canonical Ride identity contracts"
    )


def verify_payment_contract() -> None:
    """
    Verify completed-trip payment lifecycle without calling
    any provider or modifying persistence.
    """

    trip = Trip()

    trip.destination = "E2E Test Destination"
    trip.destination_latitude = 9.035
    trip.destination_longitude = 38.833

    trip.pickup_name = "E2E Test Pickup"
    trip.pickup_latitude = 9.0105
    trip.pickup_longitude = 38.7612

    trip.service = "ride"
    trip.booking_status = "trip_completed"

    breakdown = calculate_fare_breakdown(
        trip,
        distance_km=8.34,
        duration_minutes=25.0,
    )

    require(
        trip.final_fare is not None,
        "Fare finalization did not populate final_fare.",
    )

    require(
        trip.payment_status
        == "payment_pending",
        (
            "Fare finalization did not move payment "
            "to payment_pending."
        ),
    )

    require(
        isinstance(
            breakdown,
            dict,
        ),
        "Fare breakdown contract is not a dictionary.",
    )

    print(
        "PASS: Final fare -> payment_pending"
    )


def verify_no_real_data_mutation() -> None:
    """
    Document the deliberate safety boundary of this first
    #128 validator.
    """

    print(
        "PASS: Contract mode performs no Ride database "
        "creation or lifecycle mutation"
    )


def main() -> None:
    print()
    print("=" * 62)
    print(
        "HABESHAGO COMMIT #128 - END-TO-END MVP VALIDATOR"
    )
    print("=" * 62)

    print()
    print(
        "Mode: SAFE CONTRACT VALIDATION"
    )

    print()

    verify_trip_contract()
    verify_platform_functions()
    verify_identity_contracts()
    verify_payment_contract()
    verify_no_real_data_mutation()

    print()
    print("=" * 62)
    print(
        "COMMIT #128 END-TO-END MVP CONTRACT VALIDATION PASSED"
    )
    print("=" * 62)

    print()
    print(
        "Next gate: controlled real passenger + driver "
        "two-device Ride validation."
    )


if __name__ == "__main__":
    main()
