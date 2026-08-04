"""
HABESHAGO Driver Registration Service

Builds the canonical driver registration and verification
contract shared by the Telegram Bot, Telegram Mini App,
Admin Platform, and future clients.

The service reads persistent repository data and prepares
clear platform-level registration information.
"""

from app.database.driver_repository import (
    get_driver_registration_profile,
)


REGISTRATION_STATUSES = {
    "verification_pending",
    "approved",
    "rejected",
    "suspended",
}

VERIFICATION_STATUSES = {
    "pending",
    "verified",
    "rejected",
}


def _build_registration_guidance(
    registration_status: str,
) -> dict:
    """
    Return display-ready guidance for one registration status.
    """

    if registration_status == "approved":
        return {
            "label": "Approved",
            "message": (
                "Your HABESHAGO driver registration "
                "has been approved."
            ),
            "next_action": (
                "Open your Driver Dashboard and manage "
                "your availability."
            ),
            "can_operate": True,
        }

    if registration_status == "rejected":
        return {
            "label": "Rejected",
            "message": (
                "Your driver registration could not "
                "be approved."
            ),
            "next_action": (
                "Review the rejection reason and contact "
                "HABESHAGO support."
            ),
            "can_operate": False,
        }

    if registration_status == "suspended":
        return {
            "label": "Suspended",
            "message": (
                "Your HABESHAGO driver account is suspended."
            ),
            "next_action": (
                "Contact HABESHAGO support for assistance."
            ),
            "can_operate": False,
        }

    return {
        "label": "Verification Pending",
        "message": (
            "Your driver registration has been submitted "
            "and is waiting for verification."
        ),
        "next_action": (
            "HABESHAGO will notify you after the review "
            "is completed."
        ),
        "can_operate": False,
    }


def get_driver_registration_status(
    telegram_id,
):
    """
    Return the canonical registration and verification status
    for one driver.

    Return None when no driver registration exists.
    """

    registration = get_driver_registration_profile(
        telegram_id
    )

    if registration is None:
        return None

    (
        driver_id,
        full_name,
        phone_number,
        vehicle,
        vehicle_year,
        vehicle_color,
        plate_number,
        registration_status,
        identity_status,
        vehicle_status,
        submitted_at,
        verified_at,
        rejection_reason,
    ) = registration

    registration_status = (
        registration_status
        if registration_status in REGISTRATION_STATUSES
        else "verification_pending"
    )

    identity_status = (
        identity_status
        if identity_status in VERIFICATION_STATUSES
        else "pending"
    )

    vehicle_status = (
        vehicle_status
        if vehicle_status in VERIFICATION_STATUSES
        else "pending"
    )

    guidance = _build_registration_guidance(
        registration_status
    )

    return {
        "driver_id": driver_id,
        "profile": {
            "full_name": full_name,
            "phone_number": phone_number,
        },
        "vehicle": {
            "name": vehicle,
            "year": vehicle_year,
            "color": vehicle_color,
            "plate_number": plate_number,
        },
        "registration": {
            "status": registration_status,
            "label": guidance["label"],
            "submitted_at": submitted_at,
            "verified_at": verified_at,
            "rejection_reason": rejection_reason,
        },
        "verification": {
            "identity": identity_status,
            "vehicle": vehicle_status,
        },
        "guidance": {
            "message": guidance["message"],
            "next_action": guidance["next_action"],
        },
        "can_operate": guidance["can_operate"],
    }