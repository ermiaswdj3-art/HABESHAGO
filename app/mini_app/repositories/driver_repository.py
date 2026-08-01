"""
HABESHAGO Driver Repository

Provides driver data to the Mini App Dispatch Engine.

This first version uses controlled in-memory driver records.
A later production version will load drivers from the database.
"""

from app.mini_app.models import Driver


_DRIVERS = [
    Driver(
        driver_id="DRV001",
        name="Abebe Bekele",
        rating=4.9,
        vehicle="Toyota Vitz",
        plate_number="AA-12345",
        vehicle_color="White",
        latitude=8.9812,
        longitude=38.7584,
    ),
    Driver(
        driver_id="DRV002",
        name="Samuel Tesfaye",
        rating=4.8,
        vehicle="Hyundai Accent",
        plate_number="AA-23456",
        vehicle_color="Silver",
        latitude=8.9768,
        longitude=38.7641,
    ),
    Driver(
        driver_id="DRV003",
        name="Dawit Alemu",
        rating=4.7,
        vehicle="Toyota Corolla",
        plate_number="AA-34567",
        vehicle_color="Blue",
        latitude=8.9895,
        longitude=38.7509,
        is_online=True,
        is_available=False,
    ),
]


def get_all_drivers() -> list[Driver]:
    """
    Return all known drivers.
    """

    return list(_DRIVERS)


def get_available_drivers() -> list[Driver]:
    """
    Return drivers who are online and available.
    """

    return [
        driver
        for driver in _DRIVERS
        if driver.can_accept_dispatch()
    ]


def get_driver_by_id(
    driver_id: str,
) -> Driver | None:
    """
    Return one driver by identifier.
    """

    for driver in _DRIVERS:
        if driver.driver_id == driver_id:
            return driver

    return None