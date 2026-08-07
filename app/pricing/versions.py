"""
HABESHAGO Pricing Version Contracts

Defines version identifiers used to make authoritative
pricing decisions reproducible and auditable.

Pricing configuration versions are intentionally separate
from the Pricing Platform contract version.
"""

from app.pricing.exceptions import (
    PricingValidationError,
)


PRICING_CONTRACT_VERSION = "1.0"

PRICING_PLATFORM_VERSION = "2026.08.v1"


def validate_version_identifier(
    value: str,
    *,
    field_name: str,
) -> str:
    """
    Validate and normalize one required version identifier.
    """

    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise PricingValidationError(
            f"{field_name} cannot be empty."
        )

    return normalized