FUEL_BASE_FARE = 130
FUEL_PRICE_PER_KM = 16

EV_BASE_FARE = 120
EV_PRICE_PER_KM = 14

PREMIUM_BASE_FARE = 150
PREMIUM_PRICE_PER_KM = 18

DELIVERY_BASE_FARE = 100
DELIVERY_PRICE_PER_KM = 12


def calculate_fare(
    distance,
    service_type="fuel",
):
    """
    Calculate the estimated fare based on
    the selected service type.
    """

    service_type = service_type.lower()

    if service_type == "ev":
        fare = EV_BASE_FARE + (distance * EV_PRICE_PER_KM)

    elif service_type == "premium":
        fare = PREMIUM_BASE_FARE + (distance * PREMIUM_PRICE_PER_KM)

    elif service_type == "delivery":
        fare = DELIVERY_BASE_FARE + (distance * DELIVERY_PRICE_PER_KM)

    else:
        # Default: Fuel Ride
        fare = FUEL_BASE_FARE + (distance * FUEL_PRICE_PER_KM)

    return round(fare, 2)