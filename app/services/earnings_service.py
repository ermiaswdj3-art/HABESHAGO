FUEL_COMMISSION_RATE = 0.10
EV_COMMISSION_RATE = 0.10
PREMIUM_COMMISSION_RATE = 0.10
DELIVERY_COMMISSION_RATE = 0.05


def get_commission_rate(service_type="fuel"):
    """
    Return the HABESHAGO commission rate
    for the selected service type.
    """

    service_type = service_type.lower()

    if service_type == "ev":
        return EV_COMMISSION_RATE

    if service_type == "premium":
        return PREMIUM_COMMISSION_RATE

    if service_type == "delivery":
        return DELIVERY_COMMISSION_RATE

    # Default: Fuel Ride
    return FUEL_COMMISSION_RATE


def calculate_earnings(
    fare,
    service_type="fuel",
):
    """
    Split the ride fare into:

    - HABESHAGO commission
    - Driver earnings
    """

    commission_rate = get_commission_rate(service_type)

    commission_amount = round(
        fare * commission_rate,
        2,
    )

    driver_earnings = round(
        fare - commission_amount,
        2,
    )

    return {
        "fare": round(fare, 2),
        "commission_rate": commission_rate,
        "commission_percentage": int(
            commission_rate * 100
        ),
        "commission_amount": commission_amount,
        "driver_earnings": driver_earnings,
    }