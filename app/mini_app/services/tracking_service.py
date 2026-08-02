"""
HABESHAGO Driver Tracking Service

Simulates driver movement toward the passenger pickup.

This foundation will later be replaced by real GPS updates
from the Driver App.
"""

from math import asin, cos, radians, sin, sqrt

from app.mini_app.models import Driver, Trip


def calculate_distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """
    Calculate geographic distance using the
    Haversine formula.
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


def estimate_eta_minutes(
    distance_km: float,
) -> int:
    """
    Estimate driver arrival time from distance.
    """

    average_speed_kmh = 24.0

    travel_minutes = (
        distance_km / average_speed_kmh
    ) * 60

    return max(1, round(travel_minutes))


def move_driver_toward_pickup(
    driver: Driver,
    trip: Trip,
    progress_ratio: float = 0.25,
) -> Driver:
    """
    Move the driver part of the remaining distance
    toward the passenger pickup.

    Args:
        driver:
            The assigned HABESHAGO driver.

        trip:
            The active passenger trip.

        progress_ratio:
            Fraction of the remaining distance moved
            during one tracking update.

    Returns:
        The updated Driver object.
    """

    if (
        trip.pickup_latitude is None
        or trip.pickup_longitude is None
    ):
        return driver

    if progress_ratio <= 0 or progress_ratio > 1:
        raise ValueError(
            "progress_ratio must be greater than 0 "
            "and less than or equal to 1."
        )

    driver.latitude += (
        trip.pickup_latitude - driver.latitude
    ) * progress_ratio

    driver.longitude += (
        trip.pickup_longitude - driver.longitude
    ) * progress_ratio

    remaining_distance_km = calculate_distance_km(
        driver.latitude,
        driver.longitude,
        trip.pickup_latitude,
        trip.pickup_longitude,
    )

    driver.eta_minutes = estimate_eta_minutes(
        remaining_distance_km
    )

    driver.set_driver_status("arriving")

    return driver