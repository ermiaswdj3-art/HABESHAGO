"""
HABESHAGO Mini App Dispatch Adapter

Adapts the Mini App Trip contract to the canonical shared
HABESHAGO Intelligent Dispatch Platform.

The Mini App does not own driver-ranking business logic.
"""

from app.mini_app.models import (
    Driver,
    Trip,
)

from app.services.dispatch_service import (
    find_ranked_drivers as find_shared_ranked_drivers,
)

from app.services.eta_service import (
    calculate_eta,
)


def _build_mini_app_driver(
    ranked_driver: dict,
) -> Driver:
    """
    Convert one canonical dispatch result into the
    Mini App's existing Driver presentation model.
    """

    driver = Driver(
        driver_id=str(
            ranked_driver["telegram_id"]
        ),
        name=ranked_driver["name"],
        rating=float(
            ranked_driver["rating"]
        ),
        vehicle=ranked_driver["vehicle"],
        plate_number=ranked_driver["plate"],
        vehicle_color=ranked_driver["color"],
        latitude=0.0,
        longitude=0.0,
        is_online=True,
        is_available=True,
    )

    driver.eta_minutes = calculate_eta(
        ranked_driver["distance"]
    )

    return driver


def rank_available_drivers(
    trip: Trip,
) -> list[Driver]:
    """
    Return Mini App Driver models in canonical shared
    dispatch-ranking order.
    """

    if (
        trip.pickup_latitude is None
        or trip.pickup_longitude is None
    ):
        return []

    ranked_drivers = (
        find_shared_ranked_drivers(
            passenger_latitude=(
                trip.pickup_latitude
            ),
            passenger_longitude=(
                trip.pickup_longitude
            ),
        )
    )

    return [
        _build_mini_app_driver(
            ranked_driver
        )
        for ranked_driver in ranked_drivers
    ]


def find_best_driver(
    trip: Trip,
) -> Driver | None:
    """
    Return the Mini App representation of the strongest
    canonical platform driver match.
    """

    ranked_drivers = rank_available_drivers(
        trip
    )

    if not ranked_drivers:
        return None

    return ranked_drivers[0]