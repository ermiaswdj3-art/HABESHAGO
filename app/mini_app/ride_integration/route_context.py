"""
HABESHAGO Mini App Canonical Route Context

Defines the geographic boundary required before a
Mini App ride may enter authoritative Ride Platform
integration.

This contract contains verified journey endpoints only.

It deliberately does not invent:
- road-network distance;
- travel duration;
- route geometry;
- traffic conditions;
- production ETA.
"""

from dataclasses import dataclass

from app.mini_app.models import (
    Trip,
)


class MiniAppRouteContextError(ValueError):
    """
    Raised when a Mini App Trip does not contain enough
    canonical geographic information for ride integration.
    """


def _require_latitude(
    value: float,
    *,
    field_name: str,
) -> float:
    """
    Require one valid latitude.
    """

    if (
        isinstance(value, bool)
        or not isinstance(
            value,
            (
                int,
                float,
            ),
        )
    ):
        raise MiniAppRouteContextError(
            f"{field_name} must be a valid latitude."
        )

    normalized = float(
        value
    )

    if not (
        -90.0
        <= normalized
        <= 90.0
    ):
        raise MiniAppRouteContextError(
            f"{field_name} is out of range."
        )

    return normalized


def _require_longitude(
    value: float,
    *,
    field_name: str,
) -> float:
    """
    Require one valid longitude.
    """

    if (
        isinstance(value, bool)
        or not isinstance(
            value,
            (
                int,
                float,
            ),
        )
    ):
        raise MiniAppRouteContextError(
            f"{field_name} must be a valid longitude."
        )

    normalized = float(
        value
    )

    if not (
        -180.0
        <= normalized
        <= 180.0
    ):
        raise MiniAppRouteContextError(
            f"{field_name} is out of range."
        )

    return normalized


@dataclass(frozen=True)
class MiniAppRouteContext:
    """
    Immutable canonical geographic context for one
    Mini App ride request.
    """

    pickup_latitude: float
    pickup_longitude: float

    destination_latitude: float
    destination_longitude: float

    @property
    def pickup(
        self,
    ) -> tuple[float, float]:
        """
        Return the canonical pickup coordinate pair.
        """

        return (
            self.pickup_latitude,
            self.pickup_longitude,
        )

    @property
    def destination(
        self,
    ) -> tuple[float, float]:
        """
        Return the canonical destination coordinate pair.
        """

        return (
            self.destination_latitude,
            self.destination_longitude,
        )


def build_route_context(
    *,
    trip: Trip,
) -> MiniAppRouteContext:
    """
    Build canonical geographic context from one Mini App
    Trip.

    No distance, ETA, pricing, or routing assumptions are
    introduced here.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppRouteContextError(
            "trip must be a Trip."
        )

    if not trip.is_ready_for_planning():
        raise MiniAppRouteContextError(
            (
                "Trip must contain canonical pickup and "
                "destination coordinates."
            )
        )

    return MiniAppRouteContext(
        pickup_latitude=(
            _require_latitude(
                trip.pickup_latitude,
                field_name=(
                    "pickup_latitude"
                ),
            )
        ),
        pickup_longitude=(
            _require_longitude(
                trip.pickup_longitude,
                field_name=(
                    "pickup_longitude"
                ),
            )
        ),
        destination_latitude=(
            _require_latitude(
                trip.destination_latitude,
                field_name=(
                    "destination_latitude"
                ),
            )
        ),
        destination_longitude=(
            _require_longitude(
                trip.destination_longitude,
                field_name=(
                    "destination_longitude"
                ),
            )
        ),
    )