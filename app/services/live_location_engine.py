"""
HABESHAGO Live Location Engine

Evaluates the freshness and quality of
driver and passenger location updates.

Current responsibilities:
- Determine location age
- Classify locations as LIVE or STALE
- Preserve UNKNOWN status when appropriate

Future responsibilities:
- Movement detection
- Speed estimation
- Route consistency
- GPS accuracy validation
- Anti-spoofing checks
"""

from datetime import datetime, timezone

from app.constants.location_status import (
    LocationStatus,
)

from app.models.live_location import (
    LiveLocation,
)

LIVE_LOCATION_MAX_AGE_SECONDS = 600


def get_location_age_seconds(
    location: LiveLocation,
    *,
    now: datetime | None = None,
) -> float:
    """
    Return the age of a location update
    in seconds.

    Negative values are normalized to zero.
    """

    current_time = now if now is not None else datetime.now(timezone.utc)

    recorded_at = location.recorded_at

    if recorded_at.tzinfo is None:
        recorded_at = recorded_at.replace(tzinfo=timezone.utc)

    age_seconds = (current_time - recorded_at).total_seconds()

    return max(
        0.0,
        age_seconds,
    )


def evaluate_location_status(
    location: LiveLocation,
    *,
    now: datetime | None = None,
) -> str:
    """
    Return the official location status
    based on update freshness.
    """

    age_seconds = get_location_age_seconds(
        location,
        now=now,
    )

    if age_seconds <= (LIVE_LOCATION_MAX_AGE_SECONDS):
        return LocationStatus.LIVE

    return LocationStatus.STALE


def refresh_location_status(
    location: LiveLocation,
    *,
    now: datetime | None = None,
) -> LiveLocation:
    """
    Evaluate and update the location's
    current freshness status.
    """

    location.status = evaluate_location_status(
        location,
        now=now,
    )

    return location


def is_location_usable(
    location: LiveLocation,
    *,
    now: datetime | None = None,
) -> bool:
    """
    Return True only when the location
    is recent enough for live platform use.
    """

    return (
        evaluate_location_status(
            location,
            now=now,
        )
        == LocationStatus.LIVE
    )
