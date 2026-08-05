"""
HABESHAGO Dispatch Candidate Model

Represents one canonical driver candidate being evaluated
by the shared Intelligent Dispatch Platform.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class DispatchCandidate:
    """
    Driver information used by the shared
    Intelligent Dispatch Platform.
    """

    driver_id: int

    distance_km: float

    rating: float

    is_online: bool

    is_available: bool

    has_active_ride: bool

    has_pending_offer: bool = False

    score: float = 0.0

    reasons: list[str] = field(
        default_factory=list
    )

    disqualification_reason: str | None = None

    def is_eligible(self) -> bool:
        """
        Return True when this candidate may receive
        a new Ride Offer.
        """

        return (
            self.is_online
            and self.is_available
            and not self.has_active_ride
            and not self.has_pending_offer
        )