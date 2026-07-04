from app.database.driver_repository import get_available_drivers
from app.services.distance_service import calculate_distance


def find_nearest_driver(passenger_latitude, passenger_longitude):
    print("\n========== DRIVER DEBUG ==========")

    drivers = get_available_drivers()

    print("Available drivers:", drivers)

    if not drivers:
        print("No available drivers found.")
        return None

    nearest_driver = None
    shortest_distance = float("inf")

    for driver in drivers:
        print("Checking driver:", driver)

        driver_latitude = driver[7]
        driver_longitude = driver[8]

        distance = calculate_distance(
            passenger_latitude,
            passenger_longitude,
            driver_latitude,
            driver_longitude,
        )

        print("Distance:", distance)

        if distance < shortest_distance:
            shortest_distance = distance
            nearest_driver = driver

    print("Selected driver:", nearest_driver)

    return {
        "telegram_id": nearest_driver[0],
        "name": nearest_driver[1],
        "phone": nearest_driver[2],
        "vehicle": nearest_driver[3],
        "color": nearest_driver[4],
        "plate": nearest_driver[5],
        "rating": nearest_driver[6],
        "distance": round(shortest_distance, 2),
    }