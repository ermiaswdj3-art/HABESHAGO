BASE_FARE = 80
PRICE_PER_KM = 20


def calculate_fare(distance):
    """
    Calculate the estimated ride fare.
    """

    total_fare = BASE_FARE + (distance * PRICE_PER_KM)

    return round(total_fare, 2)