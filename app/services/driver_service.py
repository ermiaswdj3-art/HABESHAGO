from app.services.distance_service import calculate_distance


drivers = [
    {
        "name": "Abebe",
        "latitude": 8.960000,
        "longitude": 38.770000,
        "available": True,
        "rating": 4.9,
        "vehicle": "Toyota Vitz",
        "color": "White",
        "plate": "AA-12345",
    },
    {
        "name": "Dawit",
        "latitude": 8.950000,
        "longitude": 38.780000,
        "available": True,
        "rating": 4.8,
        "vehicle": "Hyundai Grand i10",
        "color": "Silver",
        "plate": "AA-54321",
    },
    {
        "name": "Hana",
        "latitude": 8.970000,
        "longitude": 38.760000,
        "available": False,
        "rating": 5.0,
        "vehicle": "Suzuki Dzire",
        "color": "Blue",
        "plate": "AA-67890",
    },
]


def find_nearest_driver(passenger_latitude, passenger_longitude):
    """
    Find the nearest available driver.
    """

    nearest_driver = None
    shortest_distance = float("inf")

    for driver in drivers:
        if not driver["available"]:
            continue

        distance = calculate_distance(
            passenger_latitude,
            passenger_longitude,
            driver["latitude"],
            driver["longitude"],
        )

        if distance < shortest_distance:
            shortest_distance = distance
            nearest_driver = driver

    return nearest_driver