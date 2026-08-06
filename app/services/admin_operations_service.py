"""
HABESHAGO Admin Operations Service

Builds the canonical platform-wide business operations
snapshot shared by Telegram Admin, future Web Admin,
future native clients, and authorized platform APIs.

All totals represent unique HABESHAGO business records.
Client channels must never maintain separate operational
counts for the same passenger, driver, ride, or settlement.
"""

from datetime import datetime, timezone

from app.database.admin_operations_repository import (
    get_driver_operations_summary,
    get_driver_registration_summary,
    get_passenger_operations_summary,
    get_ride_offer_operations_summary,
    get_ride_operations_summary,
    get_settlement_operations_summary,
)


def _build_operational_alerts(
    *,
    drivers: dict,
    rides: dict,
    offers: dict,
    settlements: dict,
) -> list[dict]:
    """
    Build explainable business-operation alerts.
    """

    alerts = []

    if drivers["available"] == 0:
        alerts.append(
            {
                "code": "NO_AVAILABLE_DRIVERS",
                "severity": "critical",
                "message": (
                    "No drivers are currently available "
                    "for dispatch."
                ),
            }
        )

    if rides["requested"] > 0:
        alerts.append(
            {
                "code": "RIDES_WAITING",
                "severity": "warning",
                "message": (
                    f"{rides['requested']} ride request(s) "
                    "are waiting for assignment."
                ),
            }
        )

    if offers["pending"] > 0:
        alerts.append(
            {
                "code": "PENDING_RIDE_OFFERS",
                "severity": "information",
                "message": (
                    f"{offers['pending']} Ride Offer(s) "
                    "are waiting for driver responses."
                ),
            }
        )

    if settlements["not_settled"] > 0:
        alerts.append(
            {
                "code": "UNSETTLED_COMPLETED_RIDES",
                "severity": "critical",
                "message": (
                    f"{settlements['not_settled']} "
                    "completed ride(s) require "
                    "settlement review."
                ),
            }
        )

    return alerts


def get_admin_operations_snapshot() -> dict:
    """
    Return the canonical HABESHAGO business-operations
    dashboard contract.
    """

    passengers = (
        get_passenger_operations_summary()
    )

    driver_registration = (
        get_driver_registration_summary()
    )

    driver_operations = (
        get_driver_operations_summary()
    )

    rides = (
        get_ride_operations_summary()
    )

    ride_offers = (
        get_ride_offer_operations_summary()
    )

    settlements = (
        get_settlement_operations_summary()
    )

    alerts = _build_operational_alerts(
        drivers=driver_operations,
        rides=rides,
        offers=ride_offers,
        settlements=settlements,
    )

    dispatch_ready = (
        driver_operations["available"] > 0
    )

    settlements_healthy = (
        settlements["not_settled"] == 0
    )

    return {
        "generated_at": datetime.now(
            timezone.utc
        ),
        "platform": {
            "name": "HABESHAGO",
            "record_scope": "platform",
            "source_of_truth": (
                "shared_database"
            ),
        },
        "passengers": passengers,
        "drivers": {
            "registration": (
                driver_registration
            ),
            "operations": (
                driver_operations
            ),
        },
        "rides": rides,
        "ride_offers": ride_offers,
        "settlements": settlements,
        "readiness": {
            "dispatch_ready": dispatch_ready,
            "settlements_healthy": (
                settlements_healthy
            ),
            "requires_attention": (
                len(alerts) > 0
            ),
        },
        "alerts": alerts,
        "alert_count": len(alerts),
    }