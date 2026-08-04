"""
HABESHAGO Mini App Driver Dashboard Page

Builds the driver dashboard using the canonical shared
Driver Dashboard Service.

The page only prepares display data. Business information
comes from the shared platform service.
"""

from app.mini_app.config.settings import (
    MiniAppSettings,
)

from app.mini_app.pages.app_shell import (
    get_app_shell,
)

from app.services.driver_dashboard_service import (
    get_driver_dashboard as get_shared_driver_dashboard,
)


def _get_development_driver_id() -> int | None:
    """
    Return the configured development driver ID.

    Real Telegram Mini App authentication will replace
    this development bridge during the unified Telegram
    integration milestone.
    """

    raw_driver_id = (
        MiniAppSettings.DEVELOPMENT_DRIVER_ID
    )

    if not raw_driver_id:
        return None

    try:
        return int(raw_driver_id)
    except (TypeError, ValueError):
        return None


def get_driver_dashboard(
    mode: str = "light",
):
    """
    Build the Mini App Driver Dashboard.
    """

    page = get_app_shell(mode)

    driver_id = _get_development_driver_id()

    dashboard = None

    if driver_id is not None:
        dashboard = get_shared_driver_dashboard(
            driver_id
        )

    page["title"] = "Driver Dashboard"

    page["subtitle"] = (
        "Manage your status and review your "
        "HABESHAGO driver activity."
    )

    page["driver_dashboard"] = dashboard

    page["development_driver_id"] = driver_id

    return page


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_driver_dashboard())