"""
HABESHAGO Public API Routes

Defines the official public API endpoints
for the HABESHAGO Platform.

Every public endpoint should be declared
here before implementation.
"""

from app.constants.api_versions import ApiVersion

API_PREFIX = f"/api/{ApiVersion.V1}"


class ApiRoutes:
    """
    Official HABESHAGO API routes.
    """

    HEALTH = f"{API_PREFIX}/health"

    RIDES = f"{API_PREFIX}/rides"

    DRIVERS = f"{API_PREFIX}/drivers"

    PASSENGERS = f"{API_PREFIX}/passengers"

    DISPATCH = f"{API_PREFIX}/dispatch"

    LIVE_LOCATIONS = f"{API_PREFIX}/live-locations"
