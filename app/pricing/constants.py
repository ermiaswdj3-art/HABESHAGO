"""
HABESHAGO Pricing Constants

Defines the canonical vocabulary used across the
HABESHAGO Pricing Platform.

These constants describe pricing concepts only.
They do not contain fare values or calculation rules.
"""


class PricingCurrency:
    ETB = "ETB"

    ALL = {
        ETB,
    }


class PricingServiceType:
    RIDE = "ride"

    DELIVERY = "delivery"

    ALL = {
        RIDE,
        DELIVERY,
    }


class PricingRideCategory:
    ECONOMY = "economy"

    STANDARD = "standard"

    PREMIUM = "premium"

    EV = "ev"

    MOTORCYCLE = "motorcycle"

    ALL = {
        ECONOMY,
        STANDARD,
        PREMIUM,
        EV,
        MOTORCYCLE,
    }


class PricingQuoteStatus:
    ISSUED = "issued"

    ACCEPTED = "accepted"

    EXPIRED = "expired"

    SUPERSEDED = "superseded"

    ALL = {
        ISSUED,
        ACCEPTED,
        EXPIRED,
        SUPERSEDED,
    }


class PricingComponentType:
    BASE_FARE = "base_fare"

    DISTANCE = "distance"

    TIME = "time"

    WAITING = "waiting"

    TOLL = "toll"

    AIRPORT = "airport"

    SURGE = "surge"

    DISCOUNT = "discount"

    MINIMUM_FARE_ADJUSTMENT = (
        "minimum_fare_adjustment"
    )

    ROUNDING_ADJUSTMENT = (
        "rounding_adjustment"
    )

    ALL = {
        BASE_FARE,
        DISTANCE,
        TIME,
        WAITING,
        TOLL,
        AIRPORT,
        SURGE,
        DISCOUNT,
        MINIMUM_FARE_ADJUSTMENT,
        ROUNDING_ADJUSTMENT,
    }


class PricingPolicy:
    STANDARD = "standard"

    ALL = {
        STANDARD,
    }


class SurgePolicy:
    NONE = "none"

    ALL = {
        NONE,
    }