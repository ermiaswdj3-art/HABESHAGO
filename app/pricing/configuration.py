"""
HABESHAGO Pricing Configuration Domain

Defines the immutable authoritative pricing configuration
consumed by the future Pricing Engine.

This module contains configuration data and validation only.
It performs no fare calculation.
"""

from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from decimal import Decimal

from app.pricing.constants import (
    PricingCurrency,
    PricingPolicy,
    PricingRideCategory,
    PricingRoundingPolicy,
    PricingServiceType,
    SurgePolicy,
)

from app.pricing.exceptions import (
    PricingConfigurationError,
)

from app.pricing.versions import (
    validate_version_identifier,
)


ZERO_RATE = Decimal("0.00")


def _require_config_decimal(
    value,
    *,
    field_name: str,
    allow_zero: bool = True,
) -> Decimal:
    """
    Require an exact non-negative Decimal configuration
    value.
    """

    if not isinstance(
        value,
        Decimal,
    ):
        raise PricingConfigurationError(
            f"{field_name} must be Decimal."
        )

    if value < 0:
        raise PricingConfigurationError(
            f"{field_name} cannot be negative."
        )

    if (
        not allow_zero
        and value == 0
    ):
        raise PricingConfigurationError(
            f"{field_name} must be greater than zero."
        )

    return value


def _require_config_text(
    value,
    *,
    field_name: str,
) -> str:
    """
    Require one non-empty configuration identifier.
    """

    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise PricingConfigurationError(
            f"{field_name} cannot be empty."
        )

    return normalized


def _require_config_choice(
    value: str,
    *,
    field_name: str,
    allowed_values: set[str],
) -> str:
    """
    Require one canonical configuration vocabulary value.
    """

    normalized = _require_config_text(
        value,
        field_name=field_name,
    )

    if normalized not in allowed_values:
        raise PricingConfigurationError(
            (
                f"Unsupported {field_name}: "
                f"{normalized}"
            )
        )

    return normalized


def _require_aware_datetime(
    value: datetime,
    *,
    field_name: str,
) -> datetime:
    """
    Require a timezone-aware configuration timestamp.
    """

    if not isinstance(
        value,
        datetime,
    ):
        raise PricingConfigurationError(
            f"{field_name} must be datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PricingConfigurationError(
            (
                f"{field_name} must be "
                "timezone-aware."
            )
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class PricingConfiguration:
    """
    Immutable authoritative HABESHAGO pricing configuration.

    One configuration represents one exact set of pricing
    rules for a city, service type and ride category.

    A changed pricing rule must create a new configuration
    version rather than mutate historical configuration.
    """

    configuration_version: str

    city: str

    service_type: str

    ride_category: str

    base_fare: Decimal

    price_per_km: Decimal

    price_per_minute: Decimal

    waiting_price_per_minute: Decimal

    minimum_fare: Decimal

    rounding_policy: str

    rounding_multiple: Decimal

    currency: str = PricingCurrency.ETB

    pricing_policy: str = (
        PricingPolicy.STANDARD
    )

    surge_policy: str = (
        SurgePolicy.NONE
    )

    effective_from: datetime = field(
        default_factory=lambda: (
            datetime.now(
                timezone.utc
            )
        )
    )

    effective_until: datetime | None = None

    is_active: bool = True

    configuration_id: int | None = None

    created_at: datetime | None = None

    updated_at: datetime | None = None

    def __post_init__(
        self,
    ) -> None:
        validate_version_identifier(
            self.configuration_version,
            field_name="configuration_version",
        )

        _require_config_text(
            self.city,
            field_name="city",
        )

        _require_config_choice(
            self.service_type,
            field_name="service_type",
            allowed_values=(
                PricingServiceType.ALL
            ),
        )

        _require_config_choice(
            self.ride_category,
            field_name="ride_category",
            allowed_values=(
                PricingRideCategory.ALL
            ),
        )

        _require_config_choice(
            self.currency,
            field_name="currency",
            allowed_values=(
                PricingCurrency.ALL
            ),
        )

        _require_config_choice(
            self.pricing_policy,
            field_name="pricing_policy",
            allowed_values=(
                PricingPolicy.ALL
            ),
        )

        _require_config_choice(
            self.surge_policy,
            field_name="surge_policy",
            allowed_values=(
                SurgePolicy.ALL
            ),
        )

        _require_config_choice(
            self.rounding_policy,
            field_name="rounding_policy",
            allowed_values=(
                PricingRoundingPolicy.ALL
            ),
        )

        _require_config_decimal(
            self.base_fare,
            field_name="base_fare",
        )

        _require_config_decimal(
            self.price_per_km,
            field_name="price_per_km",
        )

        _require_config_decimal(
            self.price_per_minute,
            field_name="price_per_minute",
        )

        _require_config_decimal(
            self.waiting_price_per_minute,
            field_name=(
                "waiting_price_per_minute"
            ),
        )

        _require_config_decimal(
            self.minimum_fare,
            field_name="minimum_fare",
        )

        _require_config_decimal(
            self.rounding_multiple,
            field_name="rounding_multiple",
            allow_zero=(
                self.rounding_policy
                == PricingRoundingPolicy.NONE
            ),
        )

        if (
            self.rounding_policy
            == PricingRoundingPolicy.NONE
            and self.rounding_multiple
            != 0
        ):
            raise PricingConfigurationError(
                (
                    "rounding_multiple must be zero "
                    "when rounding_policy is none."
                )
            )

        _require_aware_datetime(
            self.effective_from,
            field_name="effective_from",
        )

        if self.effective_until is not None:
            _require_aware_datetime(
                self.effective_until,
                field_name="effective_until",
            )

            if (
                self.effective_until
                <= self.effective_from
            ):
                raise PricingConfigurationError(
                    (
                        "effective_until must be later "
                        "than effective_from."
                    )
                )

        if not isinstance(
            self.is_active,
            bool,
        ):
            raise PricingConfigurationError(
                "is_active must be bool."
            )