"""
HABESHAGO API Router

Central registry for all Version 1 public
API endpoints.

Every new endpoint should be registered here.
"""

from app.constants.api_routes import ApiRoutes
from app.api.v1.health import get_health

API_ROUTER = {
    ApiRoutes.HEALTH: get_health,
}
