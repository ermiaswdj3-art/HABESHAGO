"""
HABESHAGO Pricing Exceptions

Defines the canonical error hierarchy for the
Pricing Platform.
"""


class PricingError(Exception):
    """
    Base exception for all HABESHAGO Pricing Platform
    errors.
    """


class PricingValidationError(
    PricingError
):
    """
    Raised when pricing domain input is invalid.
    """


class PricingConfigurationError(
    PricingError
):
    """
    Raised when authoritative pricing configuration is
    missing or invalid.
    """


class PricingCalculationError(
    PricingError
):
    """
    Raised when the Pricing Engine cannot safely produce
    an authoritative quote.
    """


class PricingPolicyError(
    PricingError
):
    """
    Raised when a pricing or adjustment policy is invalid.
    """


class PricingQuoteError(
    PricingError
):
    """
    Raised when an authoritative PricingQuote is invalid.
    """


class PricingQuoteExpiredError(
    PricingQuoteError
):
    """
    Raised when an expired quote is used where an active
    quote is required.
    """