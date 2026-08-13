"""
HABESHAGO Mini App Driver Dashboard Page

Builds the presentation shell for the authenticated
Telegram Mini App Driver Dashboard.

The page itself does not resolve driver identity.

Authoritative driver identity and business information are
loaded after page render through the authenticated
/api/driver/context boundary.

This prevents the Mini App from maintaining a competing
development-driver identity.
"""

from app.mini_app.pages.app_shell import (
    get_app_shell,
)


def get_driver_dashboard(
    mode: str = "light",
):
    """
    Build the Mini App Driver Dashboard presentation shell.

    Driver identity, profile, registration, vehicle,
    availability and operational information are resolved
    through authenticated HABESHAGO platform APIs after the
    Telegram Mini App has loaded.
    """

    page = get_app_shell(mode)

    page["title"] = "Driver Dashboard"

    page["subtitle"] = (
        "Manage your status and receive canonical "
        "HABESHAGO ride offers."
    )

    # Authoritative driver business context is deliberately
    # not resolved during the initial HTML page request.
    #
    # Telegram Mini App initData becomes available in the
    # browser and is then supplied to /api/driver/context.
    page["driver_dashboard"] = None
    page["driver_registration"] = None
    page["vehicle_management"] = None
    page["driver_availability"] = None

    page["driver_context_mode"] = (
        "authenticated_client"
    )

    return page


if __name__ == "__main__":
    from pprint import pprint

    pprint(
        get_driver_dashboard()
    )