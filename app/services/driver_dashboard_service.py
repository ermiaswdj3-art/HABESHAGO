from app.database.driver_repository import (
    get_driver_by_telegram_id,
)

from app.database.driver_earnings_repository import (
    get_driver_financial_summary,
    get_driver_today_summary,
    get_driver_week_summary,
    get_driver_month_summary,
)

from app.database.driver_statistics_repository import (
    get_driver_statistics,
)


def get_driver_dashboard(driver_id):
    """
    Build the complete driver dashboard.

    This service gathers information from
    multiple repositories and returns one
    dictionary for the Telegram handler.
    """

    driver = get_driver_by_telegram_id(
        driver_id
    )

    if driver is None:
        return None

    (
        full_name,
        phone_number,
        vehicle,
        vehicle_year,
        vehicle_color,
        plate_number,
        rating,
        is_available,
    ) = driver

    dashboard = {
        "profile": {
            "full_name": full_name,
            "phone_number": phone_number,
            "vehicle": vehicle,
            "vehicle_year": vehicle_year,
            "vehicle_color": vehicle_color,
            "plate_number": plate_number,
            "rating": float(rating or 0),
            "is_available": bool(is_available),
        },
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

    return dashboard