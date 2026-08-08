"""
HABESHAGO Pricing Configuration Service

Resolves the authoritative PricingConfiguration for a
pricing scope and effective moment.

Responsibilities:
- Validate lookup scope
- Resolve effective configuration versions
- Detect missing configuration
- Detect overlapping configuration conflicts
- Provide exact historical version retrieval

This service performs no fare calculation.
"""

from datetime import (
    datetime,
    timezone,
)

from app.database.pricing_configuration_repository import (
    create_pricing_configuration,
    get_pricing_configuration_by_version,
    list_pricing_configurations,
)

from app.pricing.configuration import (
    PricingConfiguration,
)

from app.pricing.constants import (
    PricingRideCategory,
    PricingServiceType,
)

from app.pricing.exceptions import (
    PricingConfigurationError,
)


def _require_lookup_text(
    value,
    *,
    field_name: str,
) -> str:
    """
    Require one non-empty configuration lookup value.
    """

    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise PricingConfigurationError(
            f"{field_name} cannot be empty."
        )

    return normalized


def _require_lookup_choice(
    value,
    *,
    field_name: str,
    allowed_values: set[str],
) -> str:
    """
    Require one canonical pricing lookup value.
    """

    normalized = _require_lookup_text(
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


def _normalize_effective_time(
    at_time: datetime | None,
) -> datetime:
    """
    Return the timezone-aware moment used for configuration
    resolution.
    """

    effective_time = (
        at_time
        if at_time is not None
        else datetime.now(
            timezone.utc
        )
    )

    if not isinstance(
        effective_time,
        datetime,
    ):
        raise PricingConfigurationError(
            "at_time must be datetime."
        )

    if (
        effective_time.tzinfo is None
        or effective_time.utcoffset() is None
    ):
        raise PricingConfigurationError(
            "at_time must be timezone-aware."
        )

    return effective_time


def _is_configuration_effective(
    configuration: PricingConfiguration,
    *,
    at_time: datetime,
) -> bool:
    """
    Return True when one active configuration is effective
    at the requested moment.
    """

    if not configuration.is_active:
        return False

    if (
        configuration.effective_from
        > at_time
    ):
        return False

    if (
        configuration.effective_until
        is not None
        and at_time
        >= configuration.effective_until
    ):
        return False

    return True


def _configuration_windows_overlap(
    first: PricingConfiguration,
    second: PricingConfiguration,
) -> bool:
    """
    Return True when two pricing configuration effective
    windows overlap.

    Effective windows use half-open semantics:

        effective_from <= moment < effective_until

    A None effective_until means the configuration has no
    scheduled end.
    """

    first_end = (
        first.effective_until
    )

    second_end = (
        second.effective_until
    )

    if (
        first_end is not None
        and first_end
        <= second.effective_from
    ):
        return False

    if (
        second_end is not None
        and second_end
        <= first.effective_from
    ):
        return False

    return True

def create_governed_pricing_configuration(
    configuration: PricingConfiguration,
) -> PricingConfiguration:
    """
    Persist one PricingConfiguration only when it does not
    create an active effective-window conflict.

    Historical and inactive configurations remain
    available for audit and reproduction.
    """

    if not isinstance(
        configuration,
        PricingConfiguration,
    ):
        raise PricingConfigurationError(
            (
                "configuration must be a "
                "PricingConfiguration."
            )
        )

    existing_version = (
        get_pricing_configuration_by_version(
            configuration.configuration_version
        )
    )

    if existing_version is not None:
        raise PricingConfigurationError(
            (
                "Pricing configuration version already "
                "exists: "
                f"{configuration.configuration_version}"
            )
        )

    if configuration.is_active:
        existing_configurations = (
            list_pricing_configurations(
                city=configuration.city,
                service_type=(
                    configuration.service_type
                ),
                ride_category=(
                    configuration.ride_category
                ),
                is_active=True,
            )
        )

        conflicts = [
            existing
            for existing
            in existing_configurations
            if _configuration_windows_overlap(
                configuration,
                existing,
            )
        ]

        if conflicts:
            conflict_versions = ", ".join(
                existing.configuration_version
                for existing in conflicts
            )

            raise PricingConfigurationError(
                (
                    "Pricing configuration effective "
                    "window overlaps an existing active "
                    "configuration: "
                    f"{conflict_versions}"
                )
            )

    return create_pricing_configuration(
        configuration
    )

def get_effective_pricing_configuration(
    *,
    city: str,
    service_type: str,
    ride_category: str,
    at_time: datetime | None = None,
) -> PricingConfiguration:
    """
    Return the single authoritative PricingConfiguration
    effective for one pricing scope and moment.

    Raises PricingConfigurationError when:
    - no configuration is effective
    - multiple configurations overlap
    """

    normalized_city = (
        _require_lookup_text(
            city,
            field_name="city",
        )
    )

    normalized_service_type = (
        _require_lookup_choice(
            service_type,
            field_name="service_type",
            allowed_values=(
                PricingServiceType.ALL
            ),
        )
    )

    normalized_ride_category = (
        _require_lookup_choice(
            ride_category,
            field_name="ride_category",
            allowed_values=(
                PricingRideCategory.ALL
            ),
        )
    )

    effective_time = (
        _normalize_effective_time(
            at_time
        )
    )

    configurations = (
        list_pricing_configurations(
            city=normalized_city,
            service_type=(
                normalized_service_type
            ),
            ride_category=(
                normalized_ride_category
            ),
            is_active=True,
        )
    )

    effective_configurations = [
        configuration
        for configuration in configurations
        if _is_configuration_effective(
            configuration,
            at_time=effective_time,
        )
    ]

    if not effective_configurations:
        raise PricingConfigurationError(
            (
                "No effective pricing configuration "
                "exists for "
                f"city={normalized_city}, "
                "service_type="
                f"{normalized_service_type}, "
                "ride_category="
                f"{normalized_ride_category}."
            )
        )

    if len(
        effective_configurations
    ) > 1:
        versions = ", ".join(
            configuration.configuration_version
            for configuration
            in effective_configurations
        )

        raise PricingConfigurationError(
            (
                "Multiple effective pricing "
                "configurations overlap for "
                f"city={normalized_city}, "
                "service_type="
                f"{normalized_service_type}, "
                "ride_category="
                f"{normalized_ride_category}: "
                f"{versions}"
            )
        )

    return effective_configurations[0]


def get_pricing_configuration(
    *,
    city: str,
    service_type: str,
    ride_category: str,
    at_time: datetime | None = None,
) -> PricingConfiguration:
    """
    PricingConfigurationProvider-compatible facade.
    """

    return get_effective_pricing_configuration(
        city=city,
        service_type=service_type,
        ride_category=ride_category,
        at_time=at_time,
    )


def get_pricing_configuration_version(
    configuration_version: str,
) -> PricingConfiguration:
    """
    Return one exact historical configuration version.

    This lookup intentionally ignores whether the
    configuration is currently active or effective.

    Historical quote reproduction requires access to the
    exact configuration originally used.
    """

    normalized_version = (
        _require_lookup_text(
            configuration_version,
            field_name=(
                "configuration_version"
            ),
        )
    )

    configuration = (
        get_pricing_configuration_by_version(
            normalized_version
        )
    )

    if configuration is None:
        raise PricingConfigurationError(
            (
                "Pricing configuration version "
                f"{normalized_version} was not found."
            )
        )

    return configuration