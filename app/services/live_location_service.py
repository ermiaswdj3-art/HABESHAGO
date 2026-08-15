"""
HABESHAGO Live Location Service

Stores and retrieves the latest live
location for platform entities.

Current responsibilities:
- Record location updates
- Retrieve latest locations
- Refresh location freshness status
- Reject stale locations when requested

Future responsibilities:
- Persistent location storage
- Location history
- Route tracking
- WebSocket broadcasting
- GPS validation
"""

from datetime import datetime, timezone

from app.models.live_location import (
    LiveLocation,
)

from app.database.driver_repository import (
    get_driver_live_location,
)

from app.services.live_location_engine import (
    is_location_usable,
    refresh_location_status,
)

_LIVE_LOCATIONS: dict[
    int,
    LiveLocation,
] = {}


def record_live_location(
    *,
    entity_id: int,
    latitude: float,
    longitude: float,
    recorded_at: datetime | None = None,
) -> LiveLocation:
    """
    Record and return the latest location
    for one platform entity.
    """

    timestamp = recorded_at if recorded_at is not None else datetime.now(timezone.utc)

    location = LiveLocation(
        entity_id=entity_id,
        latitude=latitude,
        longitude=longitude,
        recorded_at=timestamp,
    )

    refresh_location_status(location)

    _LIVE_LOCATIONS[entity_id] = location

    return location


def get_live_location(
    entity_id: int,
) -> LiveLocation | None:
    """
    Return the latest known location for
    one entity.

    Refresh its freshness status before
    returning it.
    """

    # Canonical driver GPS is shared through
    # persistence so separate HABESHAGO processes
    # observe one operational location truth.
    persisted_location = (
        get_driver_live_location(
            entity_id
        )
    )

    if persisted_location is not None:
        location = LiveLocation(
            entity_id=entity_id,
            latitude=(
                persisted_location[
                    "latitude"
                ]
            ),
            longitude=(
                persisted_location[
                    "longitude"
                ]
            ),
            recorded_at=(
                persisted_location[
                    "recorded_at"
                ]
            ),
        )

        _LIVE_LOCATIONS[
            entity_id
        ] = location

        return refresh_location_status(
            location
        )

    # Preserve process-local support for entities
    # without a canonical driver location record.
    location = _LIVE_LOCATIONS.get(
        entity_id
    )

    if location is None:
        return None

    return refresh_location_status(
        location
    )


def get_usable_live_location(
    entity_id: int,
) -> LiveLocation | None:
    """
    Return the latest location only when
    it is still fresh enough to trust.
    """

    location = get_live_location(entity_id)

    if location is None:
        return None

    if not is_location_usable(location):
        return None

    return location


def remove_live_location(
    entity_id: int,
) -> None:
    """
    Remove one entity's stored location.
    """

    _LIVE_LOCATIONS.pop(
        entity_id,
        None,
    )


def clear_live_locations() -> None:
    """
    Remove all in-memory live locations.

    Intended primarily for testing and
    controlled application resets.
    """

    _LIVE_LOCATIONS.clear()
