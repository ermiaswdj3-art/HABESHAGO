"""
HABESHAGO Health API

The health endpoint allows external systems
to verify that the HABESHAGO platform
is available and operational.
"""

from app.models.api_response import ApiResponse


def get_health() -> ApiResponse:
    """
    Returns the current platform health.
    """

    return ApiResponse(
        success=True,
        message="HABESHAGO Platform is running.",
        data={
            "status": "healthy",
            "platform": "HABESHAGO",
            "api_version": "v1",
        },
    )
