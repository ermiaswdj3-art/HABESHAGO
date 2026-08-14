"""
HABESHAGO Runtime Bridge Authentication

Authenticates trusted internal communication between
HABESHAGO runtime clients and the canonical deployed
platform.

This mechanism is for server-to-server HABESHAGO
communication only. It must never replace Telegram
Mini App passenger or driver authentication.
"""

from hmac import compare_digest

from app.config.settings import (
    HABESHAGO_RUNTIME_BRIDGE_TOKEN,
)


class RuntimeBridgeAuthenticationError(
    ValueError
):
    """
    Raised when Runtime Bridge authentication fails.
    """


def authenticate_runtime_bridge(
    supplied_token: str,
) -> None:
    """
    Require the configured Runtime Bridge secret.

    No secret value is returned or logged.
    """

    configured_token = (
        HABESHAGO_RUNTIME_BRIDGE_TOKEN
        or ""
    ).strip()

    provided_token = (
        supplied_token
        or ""
    ).strip()

    if not configured_token:
        raise RuntimeBridgeAuthenticationError(
            "HABESHAGO Runtime Bridge is not configured."
        )

    if not provided_token:
        raise RuntimeBridgeAuthenticationError(
            "HABESHAGO Runtime Bridge authentication "
            "is required."
        )

    if not compare_digest(
        configured_token,
        provided_token,
    ):
        raise RuntimeBridgeAuthenticationError(
            "HABESHAGO Runtime Bridge authentication "
            "failed."
        )
