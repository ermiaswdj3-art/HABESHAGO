"""
HABESHAGO Mini App Route Measurement Adapter

Produces one validated MiniAppRouteMeasurement from the
canonical pickup and destination coordinates already stored
on a Mini App Trip.

This is a development routing boundary.

It does not:

- trust browser fare estimates;
- trust browser ETA estimates;
- perform dispatch;
- perform pricing;
- create Ride Offers;
- create canonical Rides.

A production road-network routing provider can replace this
adapter later without changing downstream Ride Integration
contracts.
"""

from app.mini_app.models import (
    Trip,
)

from app.mini_app.ride_integration.route_context import (
    build_route_context,
)

from app.mini_app.ride_integration.route_measurement import (
    MiniAppRouteMeasurement,
)

from app.services.distance_service import (
    calculate_distance,
)


class MiniAppRouteMeasurementAdapterError(ValueError):
    """
    Raised when canonical Mini App route measurement
    cannot be produced safely.
    """


DEFAULT_AVERAGE_SPEED_KMH = 25.0


def measure_mini_app_route(
    *,
    trip: Trip,
) -> MiniAppRouteMeasurement:
    """
    Produce one deterministic development route measurement
    from canonical Mini App pickup/destination coordinates.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppRouteMeasurementAdapterError(
            "trip must be a Trip."
        )

    try:
        route = build_route_context(
            trip=trip,
        )

        distance_km = calculate_distance(
            route.pickup[0],
            route.pickup[1],
            route.destination[0],
            route.destination[1],
        )

    except (TypeError, ValueError) as exc:
        raise MiniAppRouteMeasurementAdapterError(
            str(exc)
        ) from exc

    if distance_km <= 0:
        raise MiniAppRouteMeasurementAdapterError(
            "Calculated trip distance must be positive."
        )

    duration_minutes = (
        distance_km
        / DEFAULT_AVERAGE_SPEED_KMH
        * 60.0
    )

    if duration_minutes <= 0:
        raise MiniAppRouteMeasurementAdapterError(
            "Calculated trip duration must be positive."
        )

    reference = (
        "habeshago-development-route:"
        f"{route.pickup[0]:.6f},"
        f"{route.pickup[1]:.6f}:"
        f"{route.destination[0]:.6f},"
        f"{route.destination[1]:.6f}"
    )

    return MiniAppRouteMeasurement(
        distance_km=distance_km,
        duration_minutes=duration_minutes,
        provider="habeshago-development-routing",
        measurement_reference=reference,
    )