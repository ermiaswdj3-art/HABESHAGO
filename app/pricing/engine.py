"""
HABESHAGO Core Decimal Pricing Engine

Performs deterministic authoritative fare calculation from:

    PricingRequest
    +
    already-resolved PricingConfiguration

The engine has no:
- database access
- configuration lookup
- system clock access
- network access
- Telegram dependency
- Mini App dependency
- persistence
- event publication
- surge decision logic
- discount logic
- commission logic
- settlement logic
- AI dependency

Given identical inputs, the calculated FareBreakdown is
identical.
"""

from datetime import (
    datetime,
)

from decimal import (
    Decimal,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_HALF_UP,
)

from app.pricing.configuration import (
    PricingConfiguration,
)

from app.pricing.constants import (
    PricingComponentType,
    PricingQuoteStatus,
    PricingRoundingPolicy,
)

from app.pricing.exceptions import (
    PricingCalculationError,
)

from app.pricing.models import (
    FareBreakdown,
    PricingComponent,
    PricingQuote,
    PricingRequest,
)

from app.pricing.versions import (
    PRICING_PLATFORM_VERSION,
)


ZERO = Decimal("0.00")


def _validate_pricing_scope(
    *,
    request: PricingRequest,
    configuration: PricingConfiguration,
) -> None:
    """
    Require the PricingRequest and PricingConfiguration to
    describe the same authoritative pricing scope.

    Configuration resolution belongs outside this engine.
    The engine only verifies that the supplied configuration
    actually matches the request it was asked to price.
    """

    if not isinstance(
        request,
        PricingRequest,
    ):
        raise PricingCalculationError(
            "request must be a PricingRequest."
        )

    if not isinstance(
        configuration,
        PricingConfiguration,
    ):
        raise PricingCalculationError(
            (
                "configuration must be a "
                "PricingConfiguration."
            )
        )

    mismatches = []

    if (
        request.city
        != configuration.city
    ):
        mismatches.append(
            "city"
        )

    if (
        request.service_type
        != configuration.service_type
    ):
        mismatches.append(
            "service_type"
        )

    if (
        request.ride_category
        != configuration.ride_category
    ):
        mismatches.append(
            "ride_category"
        )

    if (
        request.currency
        != configuration.currency
    ):
        mismatches.append(
            "currency"
        )

    if mismatches:
        raise PricingCalculationError(
            (
                "Pricing request and configuration "
                "scope do not match: "
                + ", ".join(
                    mismatches
                )
            )
        )


def _round_to_multiple(
    *,
    amount: Decimal,
    policy: str,
    multiple: Decimal,
) -> Decimal:
    """
    Deterministically round a non-negative Decimal amount
    according to the configuration's rounding contract.

    NONE:
        Return the amount unchanged.

    NEAREST:
        Round to the nearest configured multiple using
        ROUND_HALF_UP.

    UP:
        Round toward the next configured multiple.

    DOWN:
        Round toward the previous configured multiple.
    """

    if not isinstance(
        amount,
        Decimal,
    ):
        raise PricingCalculationError(
            "amount must be Decimal."
        )

    if not isinstance(
        multiple,
        Decimal,
    ):
        raise PricingCalculationError(
            "rounding multiple must be Decimal."
        )

    if amount < ZERO:
        raise PricingCalculationError(
            "rounding amount cannot be negative."
        )

    if policy == PricingRoundingPolicy.NONE:
        return amount

    if multiple <= ZERO:
        raise PricingCalculationError(
            (
                "rounding multiple must be greater "
                "than zero when rounding is enabled."
            )
        )

    quotient = (
        amount
        / multiple
    )

    if (
        policy
        == PricingRoundingPolicy.NEAREST
    ):
        rounded_units = (
            quotient.to_integral_value(
                rounding=ROUND_HALF_UP
            )
        )

    elif (
        policy
        == PricingRoundingPolicy.UP
    ):
        rounded_units = (
            quotient.to_integral_value(
                rounding=ROUND_CEILING
            )
        )

    elif (
        policy
        == PricingRoundingPolicy.DOWN
    ):
        rounded_units = (
            quotient.to_integral_value(
                rounding=ROUND_FLOOR
            )
        )

    else:
        raise PricingCalculationError(
            (
                "Unsupported rounding policy: "
                f"{policy}"
            )
        )

    return (
        rounded_units
        * multiple
    )


def calculate_fare_breakdown(
    *,
    request: PricingRequest,
    configuration: PricingConfiguration,
) -> FareBreakdown:
    """
    Produce the deterministic authoritative core
    FareBreakdown.

    Core formula:

        base fare
        + distance charge
        + time charge
        + waiting charge
        + toll fee
        + airport fee
        = subtotal

    Then:

        minimum-fare adjustment
        rounding adjustment
        = final authoritative fare

    No surge, discount or commission logic is applied in
    Commit #88.
    """

    _validate_pricing_scope(
        request=request,
        configuration=configuration,
    )

    base_fare = (
        configuration.base_fare
    )

    distance_charge = (
        request.distance_km
        * configuration.price_per_km
    )

    time_charge = (
        request.duration_minutes
        * configuration.price_per_minute
    )

    waiting_charge = (
        request.waiting_minutes
        * configuration.waiting_price_per_minute
    )

    toll_fee = request.toll_fee

    airport_fee = request.airport_fee

    subtotal = (
        base_fare
        + distance_charge
        + time_charge
        + waiting_charge
        + toll_fee
        + airport_fee
    )

    minimum_adjustment = max(
        configuration.minimum_fare
        - subtotal,
        ZERO,
    )

    amount_before_rounding = (
        subtotal
        + minimum_adjustment
    )

    rounded_total = (
        _round_to_multiple(
            amount=amount_before_rounding,
            policy=(
                configuration.rounding_policy
            ),
            multiple=(
                configuration.rounding_multiple
            ),
        )
    )

    rounding_adjustment = (
        rounded_total
        - amount_before_rounding
    )

    components = [
        PricingComponent(
            component_type=(
                PricingComponentType.BASE_FARE
            ),
            amount=base_fare,
            description="Configured base fare.",
        ),
        PricingComponent(
            component_type=(
                PricingComponentType.DISTANCE
            ),
            amount=distance_charge,
            description=(
                "Distance-based charge."
            ),
        ),
        PricingComponent(
            component_type=(
                PricingComponentType.TIME
            ),
            amount=time_charge,
            description=(
                "Duration-based charge."
            ),
        ),
        PricingComponent(
            component_type=(
                PricingComponentType.WAITING
            ),
            amount=waiting_charge,
            description=(
                "Billable waiting-time charge."
            ),
        ),
        PricingComponent(
            component_type=(
                PricingComponentType.TOLL
            ),
            amount=toll_fee,
            description="Road toll fee.",
        ),
        PricingComponent(
            component_type=(
                PricingComponentType.AIRPORT
            ),
            amount=airport_fee,
            description="Airport fee.",
        ),
    ]

    if minimum_adjustment != ZERO:
        components.append(
            PricingComponent(
                component_type=(
                    PricingComponentType
                    .MINIMUM_FARE_ADJUSTMENT
                ),
                amount=minimum_adjustment,
                description=(
                    "Minimum-fare adjustment."
                ),
            )
        )

    if rounding_adjustment != ZERO:
        components.append(
            PricingComponent(
                component_type=(
                    PricingComponentType
                    .ROUNDING_ADJUSTMENT
                ),
                amount=rounding_adjustment,
                description=(
                    "Configured rounding adjustment."
                ),
            )
        )

    return FareBreakdown(
        currency=request.currency,
        components=tuple(
            components
        ),
        subtotal=subtotal,
        total_fare=rounded_total,
        minimum_fare=(
            configuration.minimum_fare
        ),
        discount_total=ZERO,
        surge_total=ZERO,
    )


def create_pricing_quote(
    *,
    request: PricingRequest,
    configuration: PricingConfiguration,
    quote_id: str,
    calculated_at: datetime,
    valid_until: datetime | None = None,
) -> PricingQuote:
    """
    Wrap one deterministic FareBreakdown in an immutable
    authoritative PricingQuote.

    Quote identity and time are supplied explicitly by the
    caller so this engine does not depend on random IDs,
    the system clock or hidden external state.
    """

    breakdown = calculate_fare_breakdown(
        request=request,
        configuration=configuration,
    )

    return PricingQuote(
        request_id=request.request_id,
        breakdown=breakdown,
        pricing_version=(
            PRICING_PLATFORM_VERSION
        ),
        configuration_version=(
            configuration.configuration_version
        ),
        pricing_policy=(
            configuration.pricing_policy
        ),
        surge_policy=(
            configuration.surge_policy
        ),
        status=(
            PricingQuoteStatus.ISSUED
        ),
        quote_id=quote_id,
        calculated_at=calculated_at,
        valid_until=valid_until,
    )