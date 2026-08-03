"""
HABESHAGO Fare Breakdown Service

Calculates and stores a transparent final fare breakdown
for a completed trip.

This foundation uses controlled pricing inputs.
Future versions will receive real distance, duration,
waiting time, zones, tolls, surge, and promotions.
"""

from typing import Any

from app.mini_app.models import Trip


CATEGORY_PRICING = {
    "economy": {
        "base_fare": 130.0,
        "distance_rate": 16.0,
        "time_rate": 2.0,
        "minimum_fare": 150.0,
    },
    "standard": {
        "base_fare": 140.0,
        "distance_rate": 17.0,
        "time_rate": 2.5,
        "minimum_fare": 165.0,
    },
    "premium": {
        "base_fare": 150.0,
        "distance_rate": 18.0,
        "time_rate": 3.0,
        "minimum_fare": 190.0,
    },
    "ev": {
        "base_fare": 120.0,
        "distance_rate": 14.0,
        "time_rate": 2.0,
        "minimum_fare": 140.0,
    },
}


def _get_category_pricing(
    category: str | None,
) -> dict[str, float]:
    """
    Return pricing rules for the selected ride category.
    """

    category_key = str(category or "economy").lower()

    return CATEGORY_PRICING.get(
        category_key,
        CATEGORY_PRICING["economy"],
    )


def calculate_fare_breakdown(
    trip: Trip,
    distance_km: float = 4.0,
    duration_minutes: float = 12.0,
    waiting_minutes: float = 0.0,
    airport_fee: float = 0.0,
    toll_fee: float = 0.0,
    discount: float = 0.0,
) -> dict[str, Any]:
    """
    Calculate a transparent final fare breakdown.

    Args:
        trip:
            The completed HABESHAGO trip.

        distance_km:
            Controlled or routed trip distance.

        duration_minutes:
            Controlled or measured trip duration.

        waiting_minutes:
            Billable waiting time.

        airport_fee:
            Optional airport surcharge.

        toll_fee:
            Optional road toll charge.

        discount:
            Optional promotion or loyalty discount.
    """

    if trip.booking_status != "trip_completed":
        raise ValueError(
            "Final fare can be calculated only after "
            "the trip is completed."
        )

    if distance_km < 0:
        raise ValueError(
            "distance_km cannot be negative."
        )

    if duration_minutes < 0:
        raise ValueError(
            "duration_minutes cannot be negative."
        )

    if waiting_minutes < 0:
        raise ValueError(
            "waiting_minutes cannot be negative."
        )

    pricing = _get_category_pricing(
        trip.category
    )

    base_fare = pricing["base_fare"]

    distance_fare = (
        distance_km
        * pricing["distance_rate"]
    )

    time_fare = (
        duration_minutes
        * pricing["time_rate"]
    )

    waiting_rate_per_minute = 2.0

    waiting_charge = (
        waiting_minutes
        * waiting_rate_per_minute
    )

    subtotal = (
        base_fare
        + distance_fare
        + time_fare
        + waiting_charge
        + airport_fee
        + toll_fee
    )

    minimum_fare = pricing["minimum_fare"]

    fare_before_discount = max(
        subtotal,
        minimum_fare,
    )

    applied_discount = min(
        max(discount, 0.0),
        fare_before_discount,
    )

    final_fare = (
        fare_before_discount
        - applied_discount
    )

    breakdown = {
        "base_fare": round(base_fare, 2),
        "distance_fare": round(
            distance_fare,
            2,
        ),
        "time_fare": round(
            time_fare,
            2,
        ),
        "waiting_charge": round(
            waiting_charge,
            2,
        ),
        "airport_fee": round(
            airport_fee,
            2,
        ),
        "toll_fee": round(
            toll_fee,
            2,
        ),
        "discount": round(
            applied_discount,
            2,
        ),
        "minimum_fare": round(
            minimum_fare,
            2,
        ),
        "final_fare": round(
            final_fare,
            2,
        ),
    }

    trip.final_fare = breakdown["final_fare"]
    trip.fare_breakdown = breakdown
    trip.set_payment_status(
        "payment_pending"
    )

    return {
        "currency": trip.fare_currency,
        "distance_km": round(
            distance_km,
            2,
        ),
        "duration_minutes": round(
            duration_minutes,
            2,
        ),
        "waiting_minutes": round(
            waiting_minutes,
            2,
        ),
        "breakdown": breakdown,
    }