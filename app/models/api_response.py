"""
HABESHAGO API Response Model

Defines the standard structure returned by
every public HABESHAGO API endpoint.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiResponse:
    """
    Standard API response.
    """

    success: bool
    message: str
    data: Any = None