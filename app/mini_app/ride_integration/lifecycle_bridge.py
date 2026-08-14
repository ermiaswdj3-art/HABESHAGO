"""
HABESHAGO Mini App Ride Lifecycle Bridge

Connects canonical Ride Offer acceptance to the Mini App
without duplicating Ride Platform responsibilities.

The shared Ride Offer Acceptance Platform remains
authoritative for:

- validating the pending Ride Offer;
- validating the accepting driver;
- atomically creating the canonical Ride;
- marking the Ride Offer accepted;
- linking accepted_ride_id to that Ride.

The Mini App integration layer then reloads that canonical
Ride and binds its identity to the presentation-level Trip.
"""

from dataclasses import dataclass

from app.mini_app.models import (
    Trip,
)

from app.constants.ride_states import (
    RideState,
)

from app.state.active_ride_state import (
    active_rides,
)

from app.mini_app.ride_integration.acceptance_adapter import (
    attach_trip_from_accepted_offer,
)

from app.mini_app.ride_integration.service import (
    MiniAppRideIntegrationResult,
)

from app.services.ride_offer_acceptance_service import (
    accept_offer_and_create_ride,
)


class MiniAppRideLifecycleBridgeError(ValueError):
    """
    Raised when the Mini App cannot safely complete
    canonical Ride Offer acceptance and Ride binding.
    """


@dataclass(frozen=True)
class MiniAppRideLifecycleResult:
    """
    Result of one canonical Ride Offer acceptance followed
    by Mini App Ride binding.
    """

    acceptance: dict
    integration: MiniAppRideIntegrationResult

    @property
    def trip(
        self,
    ) -> Trip:
        """
        Return the Mini App Trip bound to the canonical Ride.
        """

        return self.integration.trip

    @property
    def ride_id(
        self,
    ) -> int:
        """
        Return the authoritative canonical Ride ID.
        """

        return self.integration.reference.ride_id

    @property
    def passenger_id(
        self,
    ) -> int:
        """
        Return the authoritative passenger identity.
        """

        return self.integration.reference.passenger_id

    @property
    def driver_id(
        self,
    ) -> int:
        """
        Return the authoritative driver identity.
        """

        return self.integration.reference.driver_id


def accept_offer_and_bind_trip(
    *,
    trip: Trip,
    offer_id: int,
    driver_id: int,
) -> MiniAppRideLifecycleResult:
    """
    Atomically accept one canonical Ride Offer through the
    shared Ride Platform and bind the resulting canonical
    Ride to the supplied Mini App Trip.

    This function does not independently create or mutate
    Ride Platform identity.
    """

    if not isinstance(
        trip,
        Trip,
    ):
        raise MiniAppRideLifecycleBridgeError(
            "trip must be a Trip."
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
        raise MiniAppRideLifecycleBridgeError(
            "offer_id must be a positive integer."
        )

    if (
        not isinstance(
            driver_id,
            int,
        )
        or isinstance(
            driver_id,
            bool,
        )
        or driver_id <= 0
    ):
        raise MiniAppRideLifecycleBridgeError(
            "driver_id must be a positive integer."
        )

    try:
        acceptance = (
            accept_offer_and_create_ride(
                offer_id=offer_id,
                driver_id=driver_id,
            )
        )

    except ValueError as exc:
        raise MiniAppRideLifecycleBridgeError(
            str(exc)
        ) from exc

    if not isinstance(
        acceptance,
        dict,
    ):
        raise MiniAppRideLifecycleBridgeError(
            (
                "Shared Ride Offer Acceptance Platform "
                "returned an invalid result."
            )
        )

    integration = (
        attach_trip_from_accepted_offer(
            trip=trip,
            acceptance_result=acceptance,
        )
    )

    if (
        integration.reference.ride_id
        != acceptance.get(
            "ride_id"
        )
    ):
        raise MiniAppRideLifecycleBridgeError(
            (
                "Mini App Ride identity does not match "
                "the accepted canonical Ride."
            )
        )

    canonical_ride_id = (
        integration.reference.ride_id
    )

    canonical_passenger_id = (
        integration.reference.passenger_id
    )

    canonical_driver_id = (
        integration.reference.driver_id
    )

    active_rides[
        canonical_driver_id
    ] = {
        "ride_id": canonical_ride_id,
        "offer_id": acceptance.get(
            "offer_id"
        ),
        "offer_reference": acceptance.get(
            "offer_reference"
        ),
        "passenger_id": canonical_passenger_id,
        "pickup": acceptance.get(
            "pickup"
        ),
        "destination": acceptance.get(
            "destination"
        ),
        "distance": float(
            acceptance.get(
                "distance"
            )
            or 0
        ),
        "pickup_distance": float(
            acceptance.get(
                "pickup_distance"
            )
            or 0
        ),
        "pickup_eta": int(
            acceptance.get(
                "pickup_eta"
            )
            or 0
        ),
        "trip_eta": int(
            acceptance.get(
                "trip_eta"
            )
            or 0
        ),
        "fare": float(
            acceptance.get(
                "fare"
            )
            or 0
        ),
        "payment_method": (
            acceptance.get(
                "payment_method"
            )
            or "Cash"
        ),
        "service_type": (
            acceptance.get(
                "service_type"
            )
            or "ride"
        ),
        "status": (
            RideState.DRIVER_ACCEPTED
        ),
        "recovered": False,
    }

    return MiniAppRideLifecycleResult(
        acceptance=acceptance,
        integration=integration,
    )