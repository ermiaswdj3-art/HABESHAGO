"""
HABESHAGO Mini App Ride Offer Adapter

Creates one canonical shared HABESHAGO Ride Offer from
an already-validated Mini App Ride Offer context.

This adapter does not:
- authenticate passengers;
- rank drivers;
- calculate routes;
- calculate fares;
- accept ride offers;
- create rides.

Those responsibilities belong to their existing
authoritative platform services.
"""

from app.mini_app.ride_integration.ride_offer_context import (
    MiniAppRideOfferContext,
)

from app.services.ride_offer_service import (
    create_driver_ride_offer,
)


class MiniAppRideOfferAdapterError(ValueError):
    """
    Raised when canonical Ride Offer creation cannot
    proceed through the Mini App integration boundary.
    """


def create_canonical_ride_offer(
    *,
    context: MiniAppRideOfferContext,
) -> dict:
    """
    Create one persistent canonical Ride Offer through
    HABESHAGO's existing shared Ride Offer Platform.

    The returned dictionary is the canonical serialized
    Ride Offer contract produced by the shared platform.

    This adapter deliberately does not reinterpret or
    reshape that shared contract.
    """

    if not isinstance(
        context,
        MiniAppRideOfferContext,
    ):
        raise MiniAppRideOfferAdapterError(
            (
                "context must be a "
                "MiniAppRideOfferContext."
            )
        )

    try:
        offer = create_driver_ride_offer(
            passenger_id=(
                context.passenger_id
            ),
            driver_id=(
                context.driver_id
            ),
            pickup=(
                context.pickup
            ),
            destination=(
                context.destination
            ),
            distance=(
                context.distance_km
            ),
            pickup_distance=(
                context.pickup_distance_km
            ),
            pickup_eta=(
                context.pickup_eta_minutes
            ),
            trip_eta=(
                context.trip_eta_minutes
            ),
            fare=(
                context.fare
            ),
            payment_method=(
                context.payment_method
            ),
            service_type=(
                context.service_type
            ),
        )

    except ValueError as exc:
        raise MiniAppRideOfferAdapterError(
            str(exc)
        ) from exc

    if not isinstance(
        offer,
        dict,
    ):
        raise MiniAppRideOfferAdapterError(
            (
                "Shared Ride Offer Platform returned "
                "an invalid result."
            )
        )

    offer_id = offer.get(
        "offer_id"
    )

    if (
        not isinstance(
            offer_id,
            int,
        )
        or isinstance(
            offer_id,
            bool,
        )
        or offer_id <= 0
    ):
        raise MiniAppRideOfferAdapterError(
            (
                "Shared Ride Offer Platform did not "
                "return a valid canonical offer_id."
            )
        )

    return offer