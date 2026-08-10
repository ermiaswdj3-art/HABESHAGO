"""
HABESHAGO Mini App Canonical Ride Offer Orchestrator

Coordinates the trusted Mini App integration path from
dispatch candidate and route measurement to one persistent
canonical HABESHAGO Ride Offer.

Workflow:

    Authenticated Passenger
            +
    Mini App Trip
            +
    Canonical Dispatch Driver
            +
    Canonical Route Measurement
            |
            v
    Authoritative Pricing Platform
            |
            v
    Ride Offer Preparation
            |
            v
    Shared Ride Offer Platform

This orchestrator does not:

- authenticate Telegram init data;
- resolve passenger persistence;
- rank drivers;
- calculate route measurements;
- calculate fares itself;
- define pricing configuration;
- accept Ride Offers;
- create canonical Rides;
- perform payment processing;
- perform settlement.
"""

from dataclasses import dataclass
from datetime import datetime

from app.mini_app.auth import (
    AuthenticatedMiniAppPassenger,
)

from app.mini_app.models import (
    Driver,
    Trip,
)

from app.mini_app.ride_integration.offer_preparation import (
    prepare_ride_offer_context,
)

from app.mini_app.ride_integration.pricing_adapter import (
    MiniAppPricingResult,
    price_mini_app_ride,
)

from app.mini_app.ride_integration.ride_offer_adapter import (
    create_canonical_ride_offer,
)

from app.mini_app.ride_integration.ride_offer_context import (
    MiniAppRideOfferContext,
)

from app.mini_app.ride_integration.route_measurement import (
    MiniAppRouteMeasurement,
)


class MiniAppRideOfferOrchestratorError(ValueError):
    """
    Raised when canonical Mini App Ride Offer orchestration
    cannot complete safely.
    """


@dataclass(frozen=True)
class MiniAppRideOfferOrchestrationResult:
    """
    Immutable integration result for one canonical
    Mini App Ride Offer.
    """

    pricing: MiniAppPricingResult

    context: MiniAppRideOfferContext

    offer: dict


def orchestrate_mini_app_ride_offer(
    *,
    trip: Trip,
    passenger: AuthenticatedMiniAppPassenger,
    driver: Driver,
    measurement: MiniAppRouteMeasurement,
    pickup_distance_km: float,
    pickup_eta_minutes: int,
    payment_method: str,
    city: str,
    quote_id: str,
    calculated_at: datetime,
) -> MiniAppRideOfferOrchestrationResult:
    """
    Price and persist one canonical Ride Offer from
    trusted Mini App integration objects.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppRideOfferOrchestratorError(
            "trip must be a Trip."
        )

    if not isinstance(
        passenger,
        AuthenticatedMiniAppPassenger,
    ):
        raise MiniAppRideOfferOrchestratorError(
            (
                "passenger must be an "
                "AuthenticatedMiniAppPassenger."
            )
        )

    if not isinstance(
        driver,
        Driver,
    ):
        raise MiniAppRideOfferOrchestratorError(
            "driver must be a Driver."
        )

    if not isinstance(
        measurement,
        MiniAppRouteMeasurement,
    ):
        raise MiniAppRideOfferOrchestratorError(
            (
                "measurement must be a "
                "MiniAppRouteMeasurement."
            )
        )

    if trip.service != "ride":
        raise MiniAppRideOfferOrchestratorError(
            (
                "Canonical Ride Offer orchestration "
                "requires trip.service == 'ride'."
            )
        )

    if not trip.category:
        raise MiniAppRideOfferOrchestratorError(
            (
                "A canonical ride category is required "
                "before Ride Offer orchestration."
            )
        )

    try:
        pricing = price_mini_app_ride(
            passenger_id=(
                passenger.passenger_id
            ),
            driver_id=int(
                driver.driver_id
            ),
            measurement=measurement,
            service_type=trip.service,
            ride_category=trip.category,
            city=city,
            quote_id=quote_id,
            calculated_at=calculated_at,
        )

        context = prepare_ride_offer_context(
            trip=trip,
            passenger=passenger,
            driver=driver,
            measurement=measurement,
            pickup_distance_km=(
                pickup_distance_km
            ),
            pickup_eta_minutes=(
                pickup_eta_minutes
            ),
            fare=pricing.fare,
            payment_method=payment_method,
            service_type=trip.service,
        )

        offer = create_canonical_ride_offer(
            context=context,
        )

    except (TypeError, ValueError) as exc:
        raise MiniAppRideOfferOrchestratorError(
            str(exc)
        ) from exc

    return MiniAppRideOfferOrchestrationResult(
        pricing=pricing,
        context=context,
        offer=offer,
    )