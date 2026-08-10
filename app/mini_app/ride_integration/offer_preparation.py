"""
HABESHAGO Mini App Ride Offer Preparation

Prepares the validated canonical Ride Offer context needed
to cross from Mini App dispatch presentation state into the
shared HABESHAGO Ride Offer Platform.

This module does not:

- authenticate Telegram init data;
- resolve passenger identity;
- rank drivers;
- calculate routes;
- calculate fares;
- persist Ride Offers;
- accept Ride Offers;
- create canonical Rides.

Those responsibilities remain with their authoritative
platform services.
"""

from app.mini_app.auth import (
    AuthenticatedMiniAppPassenger,
)

from app.mini_app.models import (
    Driver,
    Trip,
)

from app.mini_app.ride_integration.ride_offer_context import (
    MiniAppRideOfferContext,
)

from app.mini_app.ride_integration.route_context import (
    MiniAppRouteContext,
    build_route_context,
)

from app.mini_app.ride_integration.route_measurement import (
    MiniAppRouteMeasurement,
)


class MiniAppRideOfferPreparationError(ValueError):
    """
    Raised when the Mini App does not contain enough
    trusted information to prepare a canonical Ride Offer.
    """


def prepare_ride_offer_context(
    *,
    trip: Trip,
    passenger: AuthenticatedMiniAppPassenger,
    driver: Driver,
    measurement: MiniAppRouteMeasurement,
    pickup_distance_km: float,
    pickup_eta_minutes: int,
    fare: float,
    payment_method: str,
    service_type: str,
) -> MiniAppRideOfferContext:
    """
    Build one validated Ride Offer context from trusted
    Mini App integration objects.

    The resulting context may then be supplied to the
    canonical Ride Offer adapter for persistence.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppRideOfferPreparationError(
            "trip must be a Trip."
        )

    if not isinstance(
        passenger,
        AuthenticatedMiniAppPassenger,
    ):
        raise MiniAppRideOfferPreparationError(
            (
                "passenger must be an "
                "AuthenticatedMiniAppPassenger."
            )
        )

    if not isinstance(
        driver,
        Driver,
    ):
        raise MiniAppRideOfferPreparationError(
            "driver must be a Driver."
        )

    if not isinstance(
        measurement,
        MiniAppRouteMeasurement,
    ):
        raise MiniAppRideOfferPreparationError(
            (
                "measurement must be a "
                "MiniAppRouteMeasurement."
            )
        )

    try:
        route: MiniAppRouteContext = (
           build_route_context(
               trip=trip,
            )
        )

        return MiniAppRideOfferContext(
            passenger=passenger,
            driver=driver,
            route=route,
            measurement=measurement,
            pickup_distance_km=(
                pickup_distance_km
            ),
            pickup_eta_minutes=(
                pickup_eta_minutes
            ),
            fare=fare,
            payment_method=payment_method,
            service_type=service_type,
        )

    except ValueError as exc:
        raise MiniAppRideOfferPreparationError(
            str(exc)
        ) from exc