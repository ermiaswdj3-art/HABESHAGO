"""
HABESHAGO Driver Dashboard Service

Builds the canonical driver dashboard contract shared by
the Telegram Bot, Telegram Mini App, and future clients.

The service gathers driver information from repositories.
Client pages and handlers should display this data rather
than calculating business values themselves.
"""

from app.database.driver_repository import (
    get_driver_dashboard_profile,
)

from app.database.driver_earnings_repository import (
    get_driver_financial_summary,
    get_driver_month_summary,
    get_driver_today_summary,
    get_driver_week_summary,
)

from app.database.driver_statistics_repository import (
    get_driver_statistics,
)


def _build_driver_status(
    operational_status: str,
    is_online: bool,
    is_available: bool,
    status_updated_at,
) -> dict:
    """
    Build the canonical dashboard status representation.

    operational_status is authoritative.
    The boolean flags remain compatibility information.
    """

    status_contracts = {
        "offline": {
            "code": "offline",
            "label": "You are currently offline",
            "action": "Go Online",
        },
        "available": {
            "code": "available",
            "label": "You are online and available",
            "action": "Go Offline",
        },
        "unavailable": {
            "code": "unavailable",
            "label": "You are online but unavailable",
            "action": "Go Available",
        },
    }

    status = status_contracts.get(
        operational_status,
        status_contracts["offline"],
    )

    return {
        **status,
        "operational_status": operational_status,
        "is_online": bool(is_online),
        "is_available": bool(is_available),
        "can_receive_ride_offers": (
            operational_status == "available"
        ),
        "status_updated_at": status_updated_at,
    }


def get_driver_dashboard(
    driver_id,
):
    """
    Build the complete canonical driver dashboard.

    This service is shared by every HABESHAGO client.
    """

    driver = get_driver_dashboard_profile(
        driver_id
    )

    if driver is None:
        return None

    (
        telegram_id,
        full_name,
        phone_number,
        vehicle,
        vehicle_year,
        vehicle_color,
        plate_number,
        rating,
        operational_status,
        is_online,
        is_available,
        operational_status_updated_at,
    ) = driver

    status = _build_driver_status(
        operational_status=str(
            operational_status or "offline"
        ),
        is_online=bool(is_online),
        is_available=bool(is_available),
        status_updated_at=(
            operational_status_updated_at
        ),
    )

    return {
        "driver_id": telegram_id,
        "profile": {
            "full_name": full_name,
            "phone_number": phone_number,
            "rating": float(rating or 0),
        },
        "vehicle": {
            "name": vehicle,
            "year": vehicle_year,
            "color": vehicle_color,
            "plate_number": plate_number,
        },
        "status": status,
        "today": get_driver_today_summary(
            driver_id
        ),
        "week": get_driver_week_summary(
            driver_id
        ),
        "month": get_driver_month_summary(
            driver_id
        ),
        "lifetime": get_driver_financial_summary(
            driver_id
        ),
        "statistics": get_driver_statistics(
            driver_id
        ),
    }