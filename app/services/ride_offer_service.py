"""
HABESHAGO Ride Offer Service

Owns the shared business rules for creating, reading,
accepting, rejecting, expiring, and cancelling ride offers.

Every HABESHAGO client must use this service rather than
writing ride-offer records directly.
"""

from datetime import datetime, timezone
from secrets import token_hex

from app.constants.offer_status import (
    EXPIRED,
    PENDING,
)

from app.database.ride_offer_repository import (
    accept_ride_offer,
    cancel_ride_offer,
    create_ride_offer,
    expire_due_ride_offers,
    expire_ride_offer,
    get_pending_offer_for_driver,
    get_pending_offer_for_passenger,
    get_ride_offer,
    reject_ride_offer,
)

from app.models import (
    RideOffer,
)


DEFAULT_OFFER_EXPIRATION_SECONDS = 30


def _generate_offer_reference() -> str:
    """
    Generate a unique, human-readable offer reference.
    """

    date_code = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d")

    random_code = token_hex(
        5
    ).upper()

    return (
        f"OFFER-{date_code}-{random_code}"
    )


def _serialize_ride_offer(
    offer: RideOffer,
) -> dict:
    """
    Convert a RideOffer model into a shared contract.
    """

    return {
        "offer_id": offer.offer_id,
        "offer_reference": (
            offer.offer_reference
        ),
        "passenger_id": offer.passenger_id,
        "driver_id": offer.driver_id,
        "pickup": {
            "latitude": offer.pickup_latitude,
            "longitude": offer.pickup_longitude,
        },
        "destination": {
            "latitude": (
                offer.destination_latitude
            ),
            "longitude": (
                offer.destination_longitude
            ),
        },
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
        "status": offer.status,
        "accepted_ride_id": (
            offer.accepted_ride_id
        ),
        "created_at": offer.created_at,
        "expires_at": offer.expires_at,
        "accepted_at": offer.accepted_at,
        "rejected_at": offer.rejected_at,
        "expired_at": offer.expired_at,
        "cancelled_at": offer.cancelled_at,
        "is_pending": offer.is_pending(),
        "is_terminal": offer.is_terminal(),
        "can_be_accepted": (
            offer.can_be_accepted()
        ),
    }


def create_driver_ride_offer(
    passenger_id: int,
    driver_id: int,
    pickup: tuple[float, float],
    destination: tuple[float, float],
    distance: float,
    pickup_distance: float,
    pickup_eta: int,
    trip_eta: int,
    fare: float,
    payment_method: str = "Cash",
    service_type: str = "fuel",
    expiration_seconds: int = (
        DEFAULT_OFFER_EXPIRATION_SECONDS
    ),
) -> dict:
    """
    Create one canonical pending offer.

    A driver and passenger may each have at most one
    pending offer at a time.
    """

    if len(pickup) != 2:
        raise ValueError(
            "pickup must contain latitude "
            "and longitude."
        )

    if len(destination) != 2:
        raise ValueError(
            "destination must contain latitude "
            "and longitude."
        )

    existing_driver_offer = (
        get_pending_offer_for_driver(
            driver_id
        )
    )

    if existing_driver_offer is not None:
        raise ValueError(
            "The driver already has a pending "
            "ride offer."
        )

    existing_passenger_offer = (
        get_pending_offer_for_passenger(
            passenger_id
        )
    )

    if existing_passenger_offer is not None:
        raise ValueError(
            "The passenger already has a pending "
            "ride offer."
        )

    offer = create_ride_offer(
        offer_reference=(
            _generate_offer_reference()
        ),
        passenger_id=passenger_id,
        driver_id=driver_id,
        pickup_latitude=float(
            pickup[0]
        ),
        pickup_longitude=float(
            pickup[1]
        ),
        destination_latitude=float(
            destination[0]
        ),
        destination_longitude=float(
            destination[1]
        ),
        distance=float(distance),
        pickup_distance=float(
            pickup_distance
        ),
        pickup_eta=int(pickup_eta),
        trip_eta=int(trip_eta),
        fare=float(fare),
        payment_method=str(
            payment_method or "Cash"
        ),
        service_type=str(
            service_type or "fuel"
        ),
        expiration_seconds=int(
            expiration_seconds
        ),
    )

    return _serialize_ride_offer(
        offer
    )


def get_offer(
    offer_id: int,
) -> dict | None:
    """
    Return one canonical offer contract.
    """

    offer = get_ride_offer(
        offer_id
    )

    if offer is None:
        return None

    if (
        offer.status == PENDING
        and offer.expires_at is not None
    ):
        expired_count = (
            expire_due_ride_offers()
        )

        if expired_count > 0:
            offer = get_ride_offer(
                offer_id
            )

    if offer is None:
        return None

    return _serialize_ride_offer(
        offer
    )


def get_driver_pending_offer(
    driver_id: int,
) -> dict | None:
    """
    Return the driver's current non-expired offer.
    """

    expire_due_ride_offers()

    offer = get_pending_offer_for_driver(
        driver_id
    )

    if offer is None:
        return None

    return _serialize_ride_offer(
        offer
    )


def get_passenger_pending_offer(
    passenger_id: int,
) -> dict | None:
    """
    Return the passenger's current non-expired offer.
    """

    expire_due_ride_offers()

    offer = get_pending_offer_for_passenger(
        passenger_id
    )

    if offer is None:
        return None

    return _serialize_ride_offer(
        offer
    )


def accept_driver_ride_offer(
    offer_id: int,
    accepted_ride_id: int,
) -> dict:
    """
    Accept one pending, non-expired offer.
    """

    offer = accept_ride_offer(
        offer_id=offer_id,
        accepted_ride_id=accepted_ride_id,
    )

    return _serialize_ride_offer(
        offer
    )


def reject_driver_ride_offer(
    offer_id: int,
) -> dict:
    """
    Reject one pending offer.
    """

    offer = reject_ride_offer(
        offer_id
    )

    return _serialize_ride_offer(
        offer
    )


def expire_driver_ride_offer(
    offer_id: int,
) -> dict:
    """
    Explicitly expire one pending offer.
    """

    offer = expire_ride_offer(
        offer_id
    )

    return _serialize_ride_offer(
        offer
    )


def cancel_driver_ride_offer(
    offer_id: int,
) -> dict:
    """
    Cancel one pending offer.
    """

    offer = cancel_ride_offer(
        offer_id
    )

    return _serialize_ride_offer(
        offer
    )


def expire_due_offers() -> int:
    """
    Expire all overdue pending offers.
    """

    return expire_due_ride_offers()