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
    is_online: bool,
    is_available: bool,
) -> dict:
    """
    Build the canonical dashboard status representation.
    """

    if not is_online:
        return {
            "code": "offline",
            "label": "You are currently offline",
            "action": "Go Online",
            "is_online": False,
            "is_available": False,
        }

    if is_available:
        return {
            "code": "available",
            "label": "You are online and available",
            "action": "Go Offline",
            "is_online": True,
            "is_available": True,
        }

    return {
        "code": "unavailable",
        "label": "You are online but unavailable",
        "action": "Go Available",
        "is_online": True,
        "is_available": False,
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
        is_online,
        is_available,
    ) = driver

    status = _build_driver_status(
        is_online=bool(is_online),
        is_available=bool(is_available),
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