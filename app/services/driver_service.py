from app.database.driver_repository import get_available_drivers


def find_nearest_driver(passenger_latitude, passenger_longitude):
    """
    Return the first available driver from the database.
    (We'll add true nearest-driver matching in the next upgrade.)
    """

    drivers = get_available_drivers()

    if not drivers:
        return None

    driver = drivers[0]

    return {
        "telegram_id": driver[0],
        "name": driver[1],
        "phone": driver[2],
        "vehicle": driver[3],
        "color": driver[4],
        "plate": driver[5],
        "rating": driver[6],
    }