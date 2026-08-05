"""
HABESHAGO Driver Availability Service

Owns the business rules for driver operational-state
transitions.

All clients must use this service rather than changing
driver availability directly in the database.
"""

from app.database.driver_repository import (
    get_driver_operational_state,
    set_driver_operational_status,
)

from app.services.driver_registration_service import (
    get_driver_registration_status,
)

from app.services.vehicle_management_service import (
    get_driver_vehicle_management,
)

from app.state.active_ride_state import (
    active_rides,
)


ALLOWED_DRIVER_STATUSES = {
    "offline",
    "available",
    "unavailable",
}


def _validate_driver_eligibility(
    driver_id: int,
) -> None:
    """
    Confirm that a driver is eligible to operate.

    A driver must have:
    - an approved registration;
    - verified identity;
    - a verified active vehicle.
    """

    registration = (
        get_driver_registration_status(
            driver_id
        )
    )

    if registration is None:
        raise ValueError(
            "Driver registration was not found."
        )

    registration_status = registration[
        "registration"
    ]["status"]

    identity_status = registration[
        "verification"
    ]["identity"]

    vehicle_verification_status = registration[
        "verification"
    ]["vehicle"]

    if registration_status != "approved":
        raise ValueError(
            "Your driver registration must be "
            "approved before going online."
        )

    if identity_status != "verified":
        raise ValueError(
            "Your identity must be verified before "
            "going online."
        )

    if vehicle_verification_status != "verified":
        raise ValueError(
            "Your vehicle verification must be "
            "completed before going online."
        )

    vehicle_management = (
        get_driver_vehicle_management(
            driver_id
        )
    )

    active_vehicle = vehicle_management[
        "active_vehicle"
    ]

    if active_vehicle is None:
        raise ValueError(
            "No active vehicle is registered."
        )

    if not active_vehicle["can_operate"]:
        raise ValueError(
            "Your active vehicle is not eligible "
            "for HABESHAGO operations."
        )


def _driver_has_active_ride(
    driver_id: int,
) -> bool:
    """
    Return True when the driver has an active ride.
    """

    return driver_id in active_rides


def get_driver_availability(
    driver_id: int,
) -> dict | None:
    """
    Return the canonical driver availability contract.
    """

    state = get_driver_operational_state(
        driver_id
    )

    if state is None:
        return None

    return {
        "driver_id": state.driver_id,
        "status": state.operational_status,
        "is_online": state.is_online,
        "is_available": state.is_available,
        "can_receive_ride_offers": (
            state.can_receive_ride_offers()
        ),
        "status_updated_at": (
            state.status_updated_at
        ),
        "has_active_ride": (
            _driver_has_active_ride(
                driver_id
            )
        ),
    }


def transition_driver_status(
    driver_id: int,
    target_status: str,
):
    """
    Validate and perform one canonical driver-state
    transition.

    Every operational field is persisted atomically.
    """

    if target_status not in ALLOWED_DRIVER_STATUSES:
        raise ValueError(
            "Invalid target driver status: "
            f"{target_status}"
        )

    current_state = (
        get_driver_operational_state(
            driver_id
        )
    )

    if current_state is None:
        raise ValueError(
            "Driver profile not found."
        )

    # Repeating the current transition is safe and
    # returns the existing canonical state.
    if (
        current_state.operational_status
        == target_status
    ):
        return current_state

    # Becoming operational requires complete driver
    # and vehicle eligibility.
    if target_status in {
        "available",
        "unavailable",
    }:
        _validate_driver_eligibility(
            driver_id
        )

    # A driver handling an active ride must remain
    # online. Ride lifecycle operations will release
    # the driver after completion or cancellation.
    if (
        target_status == "offline"
        and _driver_has_active_ride(
            driver_id
        )
    ):
        raise ValueError(
            "You cannot go offline while handling "
            "an active ride."
        )

    return set_driver_operational_status(
        driver_id=driver_id,
        operational_status=target_status,
    )


def make_driver_available(
    driver_id: int,
):
    """
    Put an eligible driver online and available.
    """

    return transition_driver_status(
        driver_id,
        "available",
    )


def make_driver_unavailable(
    driver_id: int,
):
    """
    Keep the driver online but stop new ride offers.

    A driver with an active ride may remain unavailable.
    """

    return transition_driver_status(
        driver_id,
        "unavailable",
    )


def make_driver_offline(
    driver_id: int,
):
    """
    Put a driver fully offline.

    Drivers with active rides cannot go offline.
    """

    return transition_driver_status(
        driver_id,
        "offline",
    )