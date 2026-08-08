"""
HABESHAGO Pricing Platform Contracts

Defines interfaces expected from Pricing Platform
components.

These contracts preserve clear boundaries between:
- configuration resolution
- deterministic pricing calculation
- quote persistence
"""

from datetime import (
    datetime,
)

from typing import (
    Protocol,
)

from app.pricing.configuration import (
    PricingConfiguration,
)

from app.pricing.models import (
    FareBreakdown,
    PricingQuote,
    PricingRequest,
)


class PricingConfigurationProvider(
    Protocol
):
    """
    Contract for retrieving authoritative versioned
    pricing configuration.
    """

    def get_pricing_configuration(
        self,
        *,
        city: str,
        service_type: str,
        ride_category: str,
        at_time: datetime | None = None,
    ) -> PricingConfiguration:
        ...


class PricingQuoteRepository(
    Protocol
):
    """
    Contract for durable PricingQuote persistence.
    """

    def save_quote(
        self,
        quote: PricingQuote,
    ) -> PricingQuote:
        ...

    def get_quote(
        self,
        quote_id: str,
    ) -> PricingQuote | None:
        ...


class PricingEngineContract(
    Protocol
):
    """
    Contract for the authoritative Core Decimal Pricing
    Engine.

    Configuration resolution occurs outside the engine.

    Implementations calculate only from the supplied
    PricingRequest and PricingConfiguration.
    """

    def calculate_fare_breakdown(
        self,
        *,
        request: PricingRequest,
        configuration: PricingConfiguration,
    ) -> FareBreakdown:
        ...

    def create_pricing_quote(
        self,
        *,
        request: PricingRequest,
        configuration: PricingConfiguration,
        quote_id: str,
        calculated_at: datetime,
        valid_until: datetime | None = None,
    ) -> PricingQuote:
        ...