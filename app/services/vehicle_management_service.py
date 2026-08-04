"""
HABESHAGO Vehicle Management Service

Builds the canonical vehicle-management contract shared by
the Telegram Bot, Telegram Mini App, Admin Platform,
Dispatch Platform, Pricing Platform, and future clients.
"""

from app.database.vehicle_repository import (
    get_active_driver_vehicle,
    get_driver_vehicles,
)


def _build_vehicle_guidance(
    verification_status: str,
    is_active: bool,
) -> dict:
    """
    Return display-ready vehicle guidance.
    """

    if verification_status == "verified":
        if is_active:
            return {
                "label": "Verified and Active",
                "message": (
                    "This vehicle is verified and currently "
                    "active for HABESHAGO operations."
                ),
                "can_operate": True,
            }

        return {
            "label": "Verified but Inactive",
            "message": (
                "This vehicle is verified but is not the "
                "driver's active operational vehicle."
            ),
            "can_operate": False,
        }

    if verification_status == "rejected":
        return {
            "label": "Verification Rejected",
            "message": (
                "This vehicle could not be approved for "
                "HABESHAGO operations."
            ),
            "can_operate": False,
        }

    if verification_status == "suspended":
        return {
            "label": "Vehicle Suspended",
            "message": (
                "This vehicle is currently suspended from "
                "HABESHAGO operations."
            ),
            "can_operate": False,
        }

    return {
        "label": "Verification Pending",
        "message": (
            "This vehicle is waiting for HABESHAGO "
            "verification."
        ),
        "can_operate": False,
    }


def _serialize_vehicle(
    vehicle,
) -> dict:
    """
    Convert a Vehicle model into a shared service contract.
    """

    guidance = _build_vehicle_guidance(
        verification_status=(
            vehicle.verification_status
        ),
        is_active=vehicle.is_active,
    )

    return {
        "vehicle_id": vehicle.vehicle_id,
        "driver_id": vehicle.driver_id,
        "display_name": vehicle.display_name,
        "vehicle_type": vehicle.vehicle_type,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "manufacturing_year": (
            vehicle.manufacturing_year
        ),
        "color": vehicle.color,
        "plate": {
            "type": vehicle.plate_type,
            "region": vehicle.plate_region,
            "number": vehicle.plate_number,
        },
        "category": vehicle.category,
        "verification_status": (
            vehicle.verification_status
        ),
        "is_active": vehicle.is_active,
        "can_operate": guidance["can_operate"],
        "status_label": guidance["label"],
        "status_message": guidance["message"],
        "created_at": vehicle.created_at,
        "updated_at": vehicle.updated_at,
    }


def get_driver_vehicle_management(
    driver_id: int,
) -> dict:
    """
    Return the canonical vehicle-management dashboard
    for one driver.
    """

    vehicles = get_driver_vehicles(
        driver_id
    )

    active_vehicle = get_active_driver_vehicle(
        driver_id
    )

    serialized_vehicles = [
        _serialize_vehicle(vehicle)
        for vehicle in vehicles
    ]

    serialized_active_vehicle = (
        _serialize_vehicle(active_vehicle)
        if active_vehicle is not None
        else None
    )

    return {
        "driver_id": driver_id,
        "active_vehicle": serialized_active_vehicle,
        "vehicles": serialized_vehicles,
        "vehicle_count": len(
            serialized_vehicles
        ),
        "has_active_vehicle": (
            serialized_active_vehicle is not None
        ),
    }