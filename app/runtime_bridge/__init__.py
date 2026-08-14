"""
HABESHAGO Runtime Bridge

Internal authenticated communication boundary between
HABESHAGO runtime clients and the canonical platform.
"""

from .auth import (
    RuntimeBridgeAuthenticationError,
    authenticate_runtime_bridge,
)

from .client import (
    RuntimeBridgeClientError,
    check_runtime_bridge_health,
    get_runtime_bridge_headers,
)


__all__ = [
    "RuntimeBridgeAuthenticationError",
    "RuntimeBridgeClientError",
    "authenticate_runtime_bridge",
    "check_runtime_bridge_health",
    "get_runtime_bridge_headers",
]
