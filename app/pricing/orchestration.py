"""
HABESHAGO Pricing Orchestration Domain

Defines the immutable authoritative result produced by
the Pricing Platform orchestration layer.

Commit #92 connects the already-established pricing
authorities without duplicating their responsibilities.

The orchestration result preserves:
- the original PricingRequest
- the exact PricingConfiguration used
- the authoritative core PricingQuote
- the governed AdjustedPricingResult
- the FinancialAllocation when requested

This module performs no pricing calculation, adjustment
decision, configuration lookup, persistence, event
publication or synchronization.
"""

from dataclasses import (
    dataclass,
)

from app.pricing.adjustments import (
    AdjustedPricingResult,
)

from app.pricing.configuration import (
    PricingConfiguration,
)

from app.pricing.exceptions import (
    PricingValidationError,
)

from app.pricing.financial import (
    FinancialAllocation,
)

from app.pricing.models import (
    PricingQuote,
    PricingRequest,
)


@dataclass(
    frozen=True,
    slots=True,
)
class PricingOrchestrationResult:
    """
    Immutable result of one authoritative HABESHAGO
    Pricing Platform orchestration.

    financial_allocation is optional because fare quotation
    can occur before a ride exists or before settlement is
    required.
    """

    request: PricingRequest

    configuration: PricingConfiguration

    quote: PricingQuote

    adjusted_result: AdjustedPricingResult

    financial_allocation: (
        FinancialAllocation | None
    ) = None

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.request,
            PricingRequest,
        ):
            raise PricingValidationError(
                "request must be a PricingRequest."
            )

        if not isinstance(
            self.configuration,
            PricingConfiguration,
        ):
            raise PricingValidationError(
                (
                    "configuration must be a "
                    "PricingConfiguration."
                )
            )

        if not isinstance(
            self.quote,
            PricingQuote,
        ):
            raise PricingValidationError(
                "quote must be a PricingQuote."
            )

        if not isinstance(
            self.adjusted_result,
            AdjustedPricingResult,
        ):
            raise PricingValidationError(
                (
                    "adjusted_result must be an "
                    "AdjustedPricingResult."
                )
            )

        if (
            self.financial_allocation
            is not None
            and not isinstance(
                self.financial_allocation,
                FinancialAllocation,
            )
        ):
            raise PricingValidationError(
                (
                    "financial_allocation must be a "
                    "FinancialAllocation or None."
                )
            )

        if (
            self.quote.request_id
            != self.request.request_id
        ):
            raise PricingValidationError(
                (
                    "Pricing quote request_id does not "
                    "match the orchestration request."
                )
            )

        if (
            self.quote.configuration_version
            != self.configuration.configuration_version
        ):
            raise PricingValidationError(
                (
                    "Pricing quote configuration_version "
                    "does not match the orchestration "
                    "configuration."
                )
            )

        if (
            self.adjusted_result.core_breakdown
            != self.quote.breakdown
        ):
            raise PricingValidationError(
                (
                    "Adjusted pricing core breakdown "
                    "must equal the authoritative quote "
                    "breakdown."
                )
            )

        if (
            self.adjusted_result.adjusted_breakdown.currency
            != self.quote.breakdown.currency
        ):
            raise PricingValidationError(
                (
                    "Adjusted pricing currency must match "
                    "the authoritative quote currency."
                )
            )

        if (
            self.financial_allocation
            is not None
            and (
                self.financial_allocation.currency
                != self.adjusted_result.adjusted_breakdown.currency
            )
        ):
            raise PricingValidationError(
                (
                    "Financial allocation currency must "
                    "match the adjusted pricing currency."
                )
            )

        if (
            self.financial_allocation
            is not None
            and (
                self.financial_allocation.passenger_fare
                != self.adjusted_result.adjusted_breakdown.total_fare
            )
        ):
            raise PricingValidationError(
                (
                    "Financial allocation passenger_fare "
                    "must equal the authoritative adjusted "
                    "fare."
                )
            )