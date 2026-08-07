"""
HABESHAGO Pricing Domain Models

Defines immutable authoritative pricing contracts shared by
Telegram, Telegram Mini App, Admin Platform, future native
applications, APIs, Settlement Platform, and other clients.

This module performs no fare calculation.
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

import uuid

from app.pricing.constants import (
    PricingComponentType,
    PricingCurrency,
    PricingPolicy,
    PricingQuoteStatus,
    PricingRideCategory,
    PricingServiceType,
    SurgePolicy,
)

from app.pricing.exceptions import (
    PricingQuoteError,
    PricingValidationError,
)

from app.pricing.versions import (
    PRICING_CONTRACT_VERSION,
    validate_version_identifier,
)


ZERO_MONEY = Decimal("0.00")


def _require_decimal(
    value,
    *,
    field_name: str,
    allow_negative: bool = False,
) -> Decimal:
    """
    Require a Decimal domain value.

    Currency and authoritative numeric pricing inputs are
    never silently converted from float.
    """

    if not isinstance(
        value,
        Decimal,
    ):
        raise PricingValidationError(
            f"{field_name} must be Decimal."
        )

    if (
        not allow_negative
        and value < 0
    ):
        raise PricingValidationError(
            f"{field_name} cannot be negative."
        )

    return value


def _require_text(
    value,
    *,
    field_name: str,
) -> str:
    """
    Validate one required text identifier.
    """

    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise PricingValidationError(
            f"{field_name} cannot be empty."
        )

    return normalized

def _require_choice(
    value: str,
    *,
    field_name: str,
    allowed_values: set[str],
) -> str:
    """
    Require one value from a canonical pricing vocabulary.
    """

    normalized = _require_text(
        value,
        field_name=field_name,
    )

    if normalized not in allowed_values:
        raise PricingValidationError(
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
    Require one timezone-aware datetime.

    Authoritative pricing timestamps must never depend on
    an ambiguous local timezone.
    """

    if not isinstance(
        value,
        datetime,
    ):
        raise PricingValidationError(
            f"{field_name} must be datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PricingValidationError(
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
class PricingRequest:
    """
    Canonical request for an authoritative HABESHAGO price.

    This model describes the facts supplied to the Pricing
    Platform. It does not calculate money.
    """

    service_type: str

    ride_category: str

    city: str

    distance_km: Decimal

    duration_minutes: Decimal

    waiting_minutes: Decimal = Decimal(
        "0"
    )

    toll_fee: Decimal = ZERO_MONEY

    airport_fee: Decimal = ZERO_MONEY

    currency: str = PricingCurrency.ETB

    passenger_id: int | None = None

    driver_id: int | None = None

    request_id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    requested_at: datetime = field(
        default_factory=lambda: (
            datetime.now(
                timezone.utc
            )
        )
    )

    contract_version: str = (
        PRICING_CONTRACT_VERSION
    )

    def __post_init__(
        self,
    ) -> None:
        _require_text(
            self.request_id,
            field_name="request_id",
        )

        _require_choice(
            self.service_type,
            field_name="service_type",
            allowed_values=(
                PricingServiceType.ALL
            ),
        )

        _require_choice(
            self.ride_category,
            field_name="ride_category",
            allowed_values=(
                PricingRideCategory.ALL
            ),
        )

        _require_text(
            self.city,
            field_name="city",
        )

        _require_choice(
            self.currency,
            field_name="currency",
            allowed_values=(
                PricingCurrency.ALL
            ),
        )

        validate_version_identifier(
            self.contract_version,
            field_name="contract_version",
        )

        _require_aware_datetime(
            self.requested_at,
            field_name="requested_at",
        )

        _require_decimal(
            self.distance_km,
            field_name="distance_km",
        )

        _require_decimal(
            self.duration_minutes,
            field_name="duration_minutes",
        )

        _require_decimal(
            self.waiting_minutes,
            field_name="waiting_minutes",
        )

        _require_decimal(
            self.toll_fee,
            field_name="toll_fee",
        )

        _require_decimal(
            self.airport_fee,
            field_name="airport_fee",
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PricingComponent:
    """
    One immutable monetary component contributing to a
    PricingQuote.
    """

    component_type: str

    amount: Decimal

    description: str = ""

    def __post_init__(
        self,
    ) -> None:
        _require_choice(
            self.component_type,
            field_name="component_type",
            allowed_values=(
                PricingComponentType.ALL
            ),
        )

        _require_decimal(
            self.amount,
            field_name="amount",
            allow_negative=True,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class FareBreakdown:
    """
    Immutable transparent monetary breakdown for one quote.

    Components may later include base fare, distance, time,
    waiting, fees, surge, discounts, minimum-fare
    adjustments and rounding adjustments.
    """

    currency: str

    components: tuple[
        PricingComponent,
        ...,
    ]

    subtotal: Decimal

    total_fare: Decimal

    minimum_fare: Decimal = ZERO_MONEY

    discount_total: Decimal = ZERO_MONEY

    surge_total: Decimal = ZERO_MONEY

    def __post_init__(
        self,
    ) -> None:
        _require_choice(
            self.currency,
            field_name="currency",
            allowed_values=(
                PricingCurrency.ALL
            ),
        )

        _require_decimal(
            self.subtotal,
            field_name="subtotal",
        )

        _require_decimal(
            self.total_fare,
            field_name="total_fare",
        )

        _require_decimal(
            self.minimum_fare,
            field_name="minimum_fare",
        )

        _require_decimal(
            self.discount_total,
            field_name="discount_total",
        )

        _require_decimal(
            self.surge_total,
            field_name="surge_total",
        )

        if not isinstance(
            self.components,
            tuple,
        ):
            raise PricingValidationError(
                "components must be a tuple."
            )

        for component in self.components:
            if not isinstance(
                component,
                PricingComponent,
            ):
                raise PricingValidationError(
                    (
                        "components must contain "
                        "PricingComponent values."
                    )
                )


@dataclass(
    frozen=True,
    slots=True,
)
class PricingQuote:
    """
    Immutable authoritative HABESHAGO PricingQuote.

    Once issued, the meaning of this quote never changes.
    A changed pricing decision must produce a new quote.
    """

    request_id: str

    breakdown: FareBreakdown

    pricing_version: str

    configuration_version: str

    pricing_policy: str = (
        PricingPolicy.STANDARD
    )

    surge_policy: str = (
        SurgePolicy.NONE
    )

    status: str = (
        PricingQuoteStatus.ISSUED
    )

    quote_id: str = field(
        default_factory=lambda: str(
            uuid.uuid4()
        )
    )

    calculated_at: datetime = field(
        default_factory=lambda: (
            datetime.now(
                timezone.utc
            )
        )
    )

    valid_until: datetime | None = None

    contract_version: str = (
        PRICING_CONTRACT_VERSION
    )

    def __post_init__(
        self,
    ) -> None:
        _require_text(
            self.quote_id,
            field_name="quote_id",
        )

        _require_text(
            self.request_id,
            field_name="request_id",
        )

        if not isinstance(
            self.breakdown,
            FareBreakdown,
        ):
            raise PricingQuoteError(
                (
                    "breakdown must be a "
                    "FareBreakdown."
                )
            )

        validate_version_identifier(
            self.pricing_version,
            field_name="pricing_version",
        )

        validate_version_identifier(
            self.configuration_version,
            field_name=(
                "configuration_version"
            ),
        )

        validate_version_identifier(
            self.contract_version,
            field_name="contract_version",
        )

        _require_aware_datetime(
            self.calculated_at,
            field_name="calculated_at",
        )

        if self.valid_until is not None:
            _require_aware_datetime(
                self.valid_until,
                field_name="valid_until",
            )

            if (
                self.valid_until
                <= self.calculated_at
            ):
                raise PricingQuoteError(
                    (
                        "valid_until must be later "
                        "than calculated_at."
                    )
                )

        _require_choice(
            self.pricing_policy,
            field_name="pricing_policy",
            allowed_values=(
                PricingPolicy.ALL
            ),
        )

        _require_choice(
            self.surge_policy,
            field_name="surge_policy",
            allowed_values=(
                SurgePolicy.ALL
            ),
        )

        _require_choice(
            self.status,
            field_name="status",
            allowed_values=(
                PricingQuoteStatus.ALL
            ),
        )

    @property
    def total_fare(
        self,
    ) -> Decimal:
        """
        Return the authoritative total fare.
        """

        return self.breakdown.total_fare

    @property
    def currency(
        self,
    ) -> str:
        """
        Return the quote currency.
        """

        return self.breakdown.currency