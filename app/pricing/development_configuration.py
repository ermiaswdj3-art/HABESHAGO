"""
HABESHAGO Development Pricing Configuration

Provides explicit development-only pricing configurations
for the Addis Ababa Ride service.

These values are migration baselines for development and
integration testing. They are not a declaration of final
commercial HABESHAGO pricing.

Configurations are persisted only through the governed
Pricing Configuration Service.
"""

from datetime import (
    datetime,
    timezone,
)
from decimal import Decimal

from app.pricing.configuration import (
    PricingConfiguration,
)

from app.pricing.configuration_service import (
    create_governed_pricing_configuration,
)

from app.pricing.exceptions import (
    PricingConfigurationError,
)

from app.pricing.constants import (
    PricingCurrency,
    PricingPolicy,
    PricingRideCategory,
    PricingRoundingPolicy,
    PricingServiceType,
    SurgePolicy,
)


DEVELOPMENT_CONFIGURATION_VERSION_PREFIX = (
    "addis-ride-development-v1"
)


def build_development_pricing_configurations(
    *,
    effective_from: datetime,
) -> tuple[
    PricingConfiguration,
    ...,
]:
    """
    Build versioned Addis Ababa development Ride pricing.

    Values preserve the existing HABESHAGO development
    pricing direction while moving pricing authority out
    of presentation-layer prototype estimates.
    """

    configurations = (
        (
            PricingRideCategory.ECONOMY,
            Decimal("130"),
            Decimal("16"),
            Decimal("2"),
            Decimal("80"),
        ),
        (
            PricingRideCategory.STANDARD,
            Decimal("140"),
            Decimal("17"),
            Decimal("2.5"),
            Decimal("90"),
        ),
        (
            PricingRideCategory.PREMIUM,
            Decimal("180"),
            Decimal("21"),
            Decimal("3"),
            Decimal("120"),
        ),
        (
            PricingRideCategory.EV,
            Decimal("150"),
            Decimal("18"),
            Decimal("2.5"),
            Decimal("100"),
        ),
    )

    return tuple(
        PricingConfiguration(
            configuration_version=(
                f"{DEVELOPMENT_CONFIGURATION_VERSION_PREFIX}-"
                f"{category}"
            ),
            city="Addis Ababa",
            service_type=PricingServiceType.RIDE,
            ride_category=category,
            currency=PricingCurrency.ETB,
            base_fare=base_fare,
            price_per_km=price_per_km,
            price_per_minute=price_per_minute,
            waiting_price_per_minute=Decimal("0"),
            minimum_fare=minimum_fare,
            rounding_policy=PricingRoundingPolicy.NEAREST,
            rounding_multiple=Decimal("1"),
            pricing_policy=PricingPolicy.STANDARD,
            surge_policy=SurgePolicy.NONE,
            effective_from=effective_from,
            effective_until=None,
            is_active=True,
        )
        for (
            category,
            base_fare,
            price_per_km,
            price_per_minute,
            minimum_fare,
        )
        in configurations
    )


def install_development_pricing_configurations(
) -> tuple[
    PricingConfiguration,
    ...,
]:
    """
    Persist missing development pricing configurations
    through the governed configuration service.
    """

    effective_from = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    created = []

    for configuration in (
        build_development_pricing_configurations(
            effective_from=effective_from,
        )
    ):
        try:
            persisted = (
                create_governed_pricing_configuration(
                    configuration
                )
            )
        except PricingConfigurationError as exc:
            if (
                "already exists"
                in str(exc).lower()
            ):
                continue

            raise

        created.append(
            persisted
        )

    return tuple(
        created
    )
