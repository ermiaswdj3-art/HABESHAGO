"""
HABESHAGO Mini App Ride Offer Preparation Context

Combines already-trusted Mini App integration inputs
before creating a canonical shared Ride Offer.

This contract performs no dispatch, pricing, routing,
payment execution, or Ride creation.
"""

from dataclasses import dataclass
from math import isfinite

from app.mini_app.auth import (
    AuthenticatedMiniAppPassenger,
)

from app.mini_app.models import (
    Driver,
)

from app.mini_app.ride_integration.route_context import (
    MiniAppRouteContext,
)

from app.mini_app.ride_integration.route_measurement import (
    MiniAppRouteMeasurement,
)


class MiniAppRideOfferContextError(ValueError):
    """
    Raised when trusted Ride Offer preparation inputs
    are incomplete or inconsistent.
    """


def _require_positive_integer(
    value,
    *,
    field_name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value <= 0
    ):
        raise MiniAppRideOfferContextError(
            f"{field_name} must be a positive integer."
        )

    return value


def _require_non_negative_number(
    value,
    *,
    field_name: str,
) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(
            value,
            (
                int,
                float,
            ),
        )
    ):
        raise MiniAppRideOfferContextError(
            f"{field_name} must be a non-negative number."
        )

    normalized = float(value)

    if (
        not isfinite(normalized)
        or normalized < 0.0
    ):
        raise MiniAppRideOfferContextError(
            f"{field_name} must be a non-negative number."
        )

    return normalized


def _require_positive_number(
    value,
    *,
    field_name: str,
) -> float:
    normalized = _require_non_negative_number(
        value,
        field_name=field_name,
    )

    if normalized <= 0.0:
        raise MiniAppRideOfferContextError(
            f"{field_name} must be a positive number."
        )

    return normalized


def _require_text(
    value,
    *,
    field_name: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise MiniAppRideOfferContextError(
            f"{field_name} must be non-empty text."
        )

    return value.strip()


@dataclass(frozen=True)
class MiniAppRideOfferContext:
    """
    Immutable trusted context required immediately before
    canonical Ride Offer creation.
    """

    passenger: AuthenticatedMiniAppPassenger
    driver: Driver
    route: MiniAppRouteContext
    measurement: MiniAppRouteMeasurement

    pickup_distance_km: float
    pickup_eta_minutes: int

    fare: float
    payment_method: str
    service_type: str

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.passenger,
            AuthenticatedMiniAppPassenger,
        ):
            raise MiniAppRideOfferContextError(
                (
                    "passenger must be an "
                    "AuthenticatedMiniAppPassenger."
                )
            )

        if not isinstance(
            self.driver,
            Driver,
        ):
            raise MiniAppRideOfferContextError(
                "driver must be a Driver."
            )

        if not isinstance(
            self.route,
            MiniAppRouteContext,
        ):
            raise MiniAppRideOfferContextError(
                "route must be a MiniAppRouteContext."
            )

        if not isinstance(
            self.measurement,
            MiniAppRouteMeasurement,
        ):
            raise MiniAppRideOfferContextError(
                (
                    "measurement must be a "
                    "MiniAppRouteMeasurement."
                )
            )

        driver_id = self.driver.driver_id

        try:
            normalized_driver_id = int(
                driver_id
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise MiniAppRideOfferContextError(
                "driver.driver_id must be a positive integer."
            ) from exc

        _require_positive_integer(
            normalized_driver_id,
            field_name="driver_id",
        )

        object.__setattr__(
            self,
            "pickup_distance_km",
            _require_non_negative_number(
                self.pickup_distance_km,
                field_name="pickup_distance_km",
            ),
        )

        pickup_eta = _require_positive_integer(
            self.pickup_eta_minutes,
            field_name="pickup_eta_minutes",
        )

        object.__setattr__(
            self,
            "pickup_eta_minutes",
            pickup_eta,
        )

        object.__setattr__(
            self,
            "fare",
            _require_positive_number(
                self.fare,
                field_name="fare",
            ),
        )

        object.__setattr__(
            self,
            "payment_method",
            _require_text(
                self.payment_method,
                field_name="payment_method",
            ),
        )

        object.__setattr__(
            self,
            "service_type",
            _require_text(
                self.service_type,
                field_name="service_type",
            ),
        )

    @property
    def passenger_id(
        self,
    ) -> int:
        return self.passenger.passenger_id

    @property
    def driver_id(
        self,
    ) -> int:
        return int(
            self.driver.driver_id
        )

    @property
    def pickup(
        self,
    ) -> tuple[float, float]:
        return self.route.pickup

    @property
    def destination(
        self,
    ) -> tuple[float, float]:
        return self.route.destination

    @property
    def distance_km(
        self,
    ) -> float:
        return self.measurement.distance_km

    @property
    def trip_eta_minutes(
        self,
    ) -> int:
        return max(
            1,
            round(
                self.measurement.duration_minutes
            ),
        )