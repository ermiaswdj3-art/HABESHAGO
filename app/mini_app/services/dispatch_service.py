"""
HABESHAGO Dispatch Service

Finds, ranks, and selects eligible drivers for an active trip.

This first version uses controlled in-memory drivers.
Future versions will use live GPS, traffic, driver state,
vehicle compatibility, offer timeouts, and reassignment.
"""

from math import asin, cos, radians, sin, sqrt

from app.mini_app.models import Driver, Trip
from app.mini_app.repositories import get_available_drivers


def calculate_distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """
    Calculate approximate geographic distance using
    the Haversine formula.
    """

    earth_radius_km = 6371.0

    latitude_difference = radians(
        latitude_2 - latitude_1
    )

    longitude_difference = radians(
        longitude_2 - longitude_1
    )

    latitude_1_radians = radians(latitude_1)
    latitude_2_radians = radians(latitude_2)

    haversine_value = (
        sin(latitude_difference / 2) ** 2
        + cos(latitude_1_radians)
        * cos(latitude_2_radians)
        * sin(longitude_difference / 2) ** 2
    )

    angular_distance = 2 * asin(
        sqrt(haversine_value)
    )

    return earth_radius_km * angular_distance


def estimate_driver_eta_minutes(
    distance_km: float,
) -> int:
    """
    Estimate driver arrival time from distance.

    Uses a controlled average city speed for the
    Dispatch Engine foundation.
    """

    average_speed_kmh = 24.0

    travel_minutes = (
        distance_km / average_speed_kmh
    ) * 60

    return max(1, round(travel_minutes))


def rank_available_drivers(
    trip: Trip,
) -> list[Driver]:
    """
    Rank eligible drivers by pickup distance first,
    then by driver rating.
    """

    if (
        trip.pickup_latitude is None
        or trip.pickup_longitude is None
    ):
        return []

    drivers = get_available_drivers()

    ranked_drivers = []

    for driver in drivers:
        distance_km = calculate_distance_km(
            trip.pickup_latitude,
            trip.pickup_longitude,
            driver.latitude,
            driver.longitude,
        )

        driver.eta_minutes = (
            estimate_driver_eta_minutes(
                distance_km
            )
        )

        ranked_drivers.append(
            (
                distance_km,
                -driver.rating,
                driver,
            )
        )

    ranked_drivers.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    return [
        item[2]
        for item in ranked_drivers
    ]


def find_best_driver(
    trip: Trip,
) -> Driver | None:
    """
    Return the highest-ranked eligible driver.
    """

    ranked_drivers = rank_available_drivers(trip)

    if not ranked_drivers:
        return None

    return ranked_drivers[0]