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

from app.services.live_location_service import (
    get_usable_live_location,
)

from app.database.admin_operations_repository import (
    get_active_ride_operations_details,
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


def _enrich_active_rides_with_live_location(
    active_rides: list[dict],
) -> list[dict]:
    """
    Enrich canonical active Ride records with the latest
    usable driver GPS from the shared Live Location
    Platform.

    SQLite remains authoritative for Ride identity,
    lifecycle, fare, route, and assignment.

    Live GPS is supplementary operational context and is
    included only while fresh enough to trust.
    """

    enriched_rides = []

    for ride in active_rides:
        enriched_ride = dict(
            ride
        )

        driver_id = ride.get(
            "driver_id"
        )

        live_location = None

        if driver_id is not None:
            live_location = (
                get_usable_live_location(
                    driver_id
                )
            )

        if live_location is None:
            enriched_ride[
                "live_location"
            ] = None

        else:
            recorded_at = (
                live_location.recorded_at
            )

            enriched_ride[
                "live_location"
            ] = {
                "latitude": (
                    live_location.latitude
                ),
                "longitude": (
                    live_location.longitude
                ),
                "status": (
                    live_location.status
                ),
                "recorded_at": (
                    recorded_at.isoformat()
                    if hasattr(
                        recorded_at,
                        "isoformat",
                    )
                    else str(recorded_at)
                ),
            }

        enriched_rides.append(
            enriched_ride
        )

    return enriched_rides


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

    active_rides = (
        get_active_ride_operations_details()
    )

    active_rides = (
        _enrich_active_rides_with_live_location(
            active_rides
        )
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
        "active_rides": active_rides,
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