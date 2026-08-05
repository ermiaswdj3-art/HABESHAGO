"""
HABESHAGO Ride Offer Recovery Service

Restores the temporary Telegram compatibility cache from
the canonical persistent Ride Offer Platform at startup.

SQLite remains authoritative.
"""

import logging

from app.database.ride_offer_repository import (
    expire_due_ride_offers,
    get_all_pending_ride_offers,
)

from app.state.driver_state import (
    pending_driver_requests,
)


logger = logging.getLogger(__name__)


def recover_pending_ride_offers() -> dict:
    """
    Expire overdue offers and rebuild the in-memory
    pending-driver compatibility cache.

    Returns recovery statistics.
    """

    expired_count = (
        expire_due_ride_offers()
    )

    pending_driver_requests.clear()

    pending_offers = (
        get_all_pending_ride_offers()
    )

    for offer in pending_offers:
        pending_driver_requests[
            offer.driver_id
        ] = {
            "offer_id": offer.offer_id,
            "offer_reference": (
                offer.offer_reference
            ),
            "passenger_id": offer.passenger_id,
            "pickup": (
                offer.pickup_latitude,
                offer.pickup_longitude,
            ),
            "destination": (
                offer.destination_latitude,
                offer.destination_longitude,
            ),
            "distance": offer.distance,
            "pickup_distance": (
                offer.pickup_distance
            ),
            "pickup_eta": offer.pickup_eta,
            "trip_eta": offer.trip_eta,
            "fare": offer.fare,
            "payment_method": (
                offer.payment_method
            ),
            "service_type": offer.service_type,
            "expires_at": offer.expires_at,
            "recovered": True,
        }

        logger.info(
            (
                "Recovered pending ride offer %s "
                "for driver %s and passenger %s."
            ),
            offer.offer_reference,
            offer.driver_id,
            offer.passenger_id,
        )

    return {
        "expired_offers": expired_count,
        "recovered_offers": len(
            pending_offers
        ),
    }