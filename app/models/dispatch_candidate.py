"""
HABESHAGO Dispatch Candidate Model

Represents one driver being evaluated
for a ride request.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class DispatchCandidate:
    """
    Driver information used by the
    Intelligent Dispatch Platform.
    """

    driver_id: int

    distance_km: float

    rating: float

    is_online: bool

    is_available: bool

    has_active_ride: bool

    score: float = 0.0

    reasons: list[str] = field(default_factory=list)
