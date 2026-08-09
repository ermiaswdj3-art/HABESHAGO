"""
HABESHAGO Payment Platform Versions

Defines explicit Payment Platform contract versions.

Version identifiers allow future payment records and
integrations to identify the contract under which they
were created.
"""


PAYMENT_PLATFORM_VERSION = (
    "2026.08.v1"
)

PAYMENT_CONTRACT_VERSION = (
    "2026.08.contract.v1"
)


def validate_payment_version(
    value,
    *,
    field_name: str,
) -> str:
    """
    Require one non-empty Payment Platform version.
    """

    if not isinstance(
        value,
        str,
    ):
        raise ValueError(
            f"{field_name} must be str."
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return normalized