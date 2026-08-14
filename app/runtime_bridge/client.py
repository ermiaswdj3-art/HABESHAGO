"""
HABESHAGO Runtime Bridge Client

Provides authenticated server-to-server communication
from a HABESHAGO runtime client to the canonical
deployed HABESHAGO runtime.
"""

from typing import Any

import requests

from app.config.settings import (
    HABESHAGO_MINI_APP_URL,
    HABESHAGO_RUNTIME_BRIDGE_TOKEN,
)


RUNTIME_BRIDGE_HEADER = (
    "X-HABESHAGO-Runtime-Bridge"
)

DEFAULT_TIMEOUT_SECONDS = 10


class RuntimeBridgeClientError(
    RuntimeError
):
    """
    Raised when the canonical Runtime Bridge cannot
    be contacted or returns an invalid response.
    """


def _require_runtime_url() -> str:
    """
    Return the configured canonical runtime URL.
    """

    runtime_url = (
        HABESHAGO_MINI_APP_URL
        or ""
    ).strip()

    if not runtime_url:
        raise RuntimeBridgeClientError(
            "HABESHAGO Mini App runtime URL "
            "is not configured."
        )

    if not runtime_url.startswith(
        "https://"
    ):
        raise RuntimeBridgeClientError(
            "HABESHAGO Runtime Bridge requires "
            "an HTTPS runtime URL."
        )

    return runtime_url.rstrip("/")


def _require_bridge_token() -> str:
    """
    Return the configured Runtime Bridge secret.
    """

    token = (
        HABESHAGO_RUNTIME_BRIDGE_TOKEN
        or ""
    ).strip()

    if not token:
        raise RuntimeBridgeClientError(
            "HABESHAGO Runtime Bridge token "
            "is not configured."
        )

    return token


def get_runtime_bridge_headers() -> dict[str, str]:
    """
    Build authenticated internal Runtime Bridge headers.
    """

    return {
        RUNTIME_BRIDGE_HEADER:
            _require_bridge_token(),
    }


def check_runtime_bridge_health(
    *,
    timeout_seconds: int = (
        DEFAULT_TIMEOUT_SECONDS
    ),
) -> dict[str, Any]:
    """
    Verify authenticated communication with the
    canonical deployed HABESHAGO runtime.
    """

    runtime_url = _require_runtime_url()

    endpoint = (
        runtime_url
        + "/api/runtime/bridge/health"
    )

    try:
        response = requests.get(
            endpoint,
            headers=get_runtime_bridge_headers(),
            timeout=timeout_seconds,
        )

    except requests.RequestException as exc:
        raise RuntimeBridgeClientError(
            "Unable to reach the HABESHAGO "
            "canonical runtime."
        ) from exc

    try:
        payload = response.json()

    except ValueError as exc:
        raise RuntimeBridgeClientError(
            "HABESHAGO canonical runtime returned "
            "a non-JSON response."
        ) from exc

    if response.status_code != 200:
        error = str(
            payload.get(
                "error",
                "Runtime Bridge request failed.",
            )
        )

        raise RuntimeBridgeClientError(
            error
        )

    if payload.get("success") is not True:
        raise RuntimeBridgeClientError(
            "HABESHAGO Runtime Bridge health "
            "response was not successful."
        )

    if (
        payload.get("canonical_runtime")
        is not True
    ):
        raise RuntimeBridgeClientError(
            "Runtime Bridge response did not identify "
            "the canonical HABESHAGO runtime."
        )

    return payload
