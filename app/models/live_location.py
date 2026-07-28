"""
HABESHAGO Live Location Model

Represents the latest known location
of a driver or passenger.
"""

from dataclasses import dataclass
from datetime import datetime

from app.constants.location_status import (
    LocationStatus,
)


@dataclass(slots=True)
class LiveLocation:
    """
    Represents one live location update.
    """

    entity_id: int

    latitude: float

    longitude: float

    recorded_at: datetime

    status: str = LocationStatus.UNKNOWN
