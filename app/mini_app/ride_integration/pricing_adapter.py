"""
HABESHAGO Mini App Pricing Adapter

Connects canonical Mini App route facts to the
authoritative HABESHAGO Pricing Platform.

This adapter:

- receives a validated canonical route measurement;
- receives trusted passenger / driver identity;
- builds one canonical PricingRequest;
- executes authoritative pricing orchestration;
- returns the final quoted fare used for Ride Offer creation.

This adapter does not:

- calculate fares itself;
- define pricing rules;
- persist pricing configurations;
- create Ride Offers;
- accept Ride Offers;
- create canonical Rides;
- perform financial settlement.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.mini_app.ride_integration.route_measurement import (
    MiniAppRouteMeasurement,
)

from app.pricing.models import (
    PricingRequest,
)

from app.pricing.orchestration import (
    PricingOrchestrationResult,
)

from app.pricing.orchestrator import (
    orchestrate_pricing,
)


class MiniAppPricingAdapterError(ValueError):
    """
    Raised when canonical Mini App pricing cannot
    proceed safely.
    """


@dataclass(frozen=True)
class MiniAppPricingResult:
    """
    Pricing result exposed to Mini App Ride Integration.
    """

    pricing: PricingOrchestrationResult

    @property
    def fare(
        self,
    ) -> float:
        """
        Return the final authoritative adjusted fare
        as a presentation-safe float.
        """

        amount = (
            self.pricing
            .adjusted_result
            .adjusted_breakdown
            .total_fare
        )

        return float(
            amount
        )

    @property
    def currency(
        self,
    ) -> str:
        """
        Return the authoritative pricing currency.
        """

        return (
            self.pricing
            .adjusted_result
            .adjusted_breakdown
            .currency
        )

    @property
    def quote_id(
        self,
    ) -> str:
        """
        Return the canonical Pricing Quote identity.
        """

        return self.pricing.quote.quote_id

    @property
    def configuration_version(
        self,
    ) -> str:
        """
        Return the pricing configuration version that
        produced this decision.
        """

        return (
            self.pricing
            .configuration
            .configuration_version
        )


def _require_positive_integer(
    value: Any,
    *,
    field_name: str,
) -> int:
    """
    Require one positive integer identifier.
    """

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value <= 0
    ):
        raise MiniAppPricingAdapterError(
            f"{field_name} must be a positive integer."
        )

    return value


def _require_text(
    value: Any,
    *,
    field_name: str,
) -> str:
    """
    Require and normalize non-empty text.
    """

    if not isinstance(
        value,
        str,
    ):
        raise MiniAppPricingAdapterError(
            f"{field_name} must be str."
        )

    normalized = value.strip()

    if not normalized:
        raise MiniAppPricingAdapterError(
            f"{field_name} cannot be empty."
        )

    return normalized


def _require_aware_datetime(
    value: Any,
    *,
    field_name: str,
) -> datetime:
    """
    Require one timezone-aware datetime.
    """

    if not isinstance(
        value,
        datetime,
    ):
        raise MiniAppPricingAdapterError(
            f"{field_name} must be datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise MiniAppPricingAdapterError(
            f"{field_name} must be timezone-aware."
        )

    return value


def price_mini_app_ride(
    *,
    passenger_id: int,
    driver_id: int,
    measurement: MiniAppRouteMeasurement,
    service_type: str,
    ride_category: str,
    city: str,
    quote_id: str,
    calculated_at: datetime,
) -> MiniAppPricingResult:
    """
    Execute authoritative pre-Ride pricing for one
    Mini App Ride Offer candidate.
    """

    passenger_id = _require_positive_integer(
        passenger_id,
        field_name="passenger_id",
    )

    driver_id = _require_positive_integer(
        driver_id,
        field_name="driver_id",
    )

    if not isinstance(
        measurement,
        MiniAppRouteMeasurement,
    ):
        raise MiniAppPricingAdapterError(
            (
                "measurement must be a "
                "MiniAppRouteMeasurement."
            )
        )

    service_type = _require_text(
        service_type,
        field_name="service_type",
    )

    ride_category = _require_text(
        ride_category,
        field_name="ride_category",
    )

    city = _require_text(
        city,
        field_name="city",
    )

    quote_id = _require_text(
        quote_id,
        field_name="quote_id",
    )

    calculated_at = _require_aware_datetime(
        calculated_at,
        field_name="calculated_at",
    )

    try:
        request = PricingRequest(
            service_type=service_type,
            ride_category=ride_category,
            city=city,
            distance_km=Decimal(
                str(
                    measurement.distance_km
                )
            ),
            duration_minutes=Decimal(
                str(
                    measurement.duration_minutes
                )
            ),
            waiting_minutes=Decimal("0"),
            toll_fee=Decimal("0"),
            airport_fee=Decimal("0"),
            currency="ETB",
            passenger_id=passenger_id,
            driver_id=driver_id,
            requested_at=calculated_at,
        )

        pricing = orchestrate_pricing(
            request=request,
            quote_id=quote_id,
            calculated_at=calculated_at,
        )

    except ValueError as exc:
        raise MiniAppPricingAdapterError(
            str(exc)
        ) from exc

    return MiniAppPricingResult(
        pricing=pricing,
    )