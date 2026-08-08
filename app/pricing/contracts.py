"""
HABESHAGO Pricing Platform Contracts

Defines interfaces expected from later Pricing Platform
components.

Commit #86 establishes contracts only.
Implementations arrive in later pricing commits.
"""

from typing import (
    Protocol,
)

from app.pricing.configuration import (
    PricingConfiguration,
)

from datetime import (
    datetime,
)

from app.pricing.models import (
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
    Contract that the future authoritative Pricing Engine
    must satisfy.

    Commit #86 intentionally provides no implementation.
    """

    def create_quote(
        self,
        request: PricingRequest,
    ) -> PricingQuote:
        ...