"""
HABESHAGO Intelligent Dispatch Engine

Evaluates driver candidates and selects
the strongest available match for a ride.

Current decision factors:
- Online status
- Availability
- Active ride status
- Distance
- Driver rating

Future decision factors:
- Idle time
- Acceptance rate
- Cancellation history
- Vehicle category
- Location freshness
- Traffic conditions
- AI-generated dispatch predictions
"""

from app.constants.dispatch_reasons import (
    DispatchReason,
)

from app.models.dispatch_candidate import (
    DispatchCandidate,
)


def calculate_candidate_score(
    candidate: DispatchCandidate,
) -> DispatchCandidate:
    """
    Calculate one driver's dispatch score.

    Drivers who are offline, unavailable,
    or already completing another ride are
    disqualified with a score of zero.
    """

    candidate.score = 0.0
    candidate.reasons.clear()

    # ==========================================
    # ELIGIBILITY RULES
    # ==========================================

    candidate.disqualification_reason = None

    if not candidate.is_online:
        candidate.disqualification_reason = (
            DispatchReason.DRIVER_OFFLINE
        )
        return candidate

    if not candidate.is_available:
        candidate.disqualification_reason = (
            DispatchReason.DRIVER_UNAVAILABLE
        )
        return candidate

    if candidate.has_active_ride:
        candidate.disqualification_reason = (
            DispatchReason.DRIVER_HAS_ACTIVE_RIDE
        )
        return candidate

    if candidate.has_pending_offer:
        candidate.disqualification_reason = (
            DispatchReason.DRIVER_HAS_PENDING_OFFER
        )
        return candidate

    candidate.reasons.append(
        DispatchReason.AVAILABLE_DRIVER
    )

    # ==========================================
    # DISTANCE SCORE
    # ==========================================

    distance_score = max(
        0.0,
        100.0 - candidate.distance_km * 10.0,
    )

    candidate.score += distance_score

    candidate.reasons.append(DispatchReason.NEAREST_DRIVER)

    # ==========================================
    # DRIVER-RATING SCORE
    # ==========================================

    rating_score = max(
        0.0,
        min(
            candidate.rating,
            5.0,
        )
        * 10.0,
    )

    candidate.score += rating_score

    candidate.reasons.append(DispatchReason.RATING_SCORE_APPLIED)

    candidate.reasons.append(DispatchReason.BEST_MATCH)

    return candidate


def rank_candidates(
    candidates: list[DispatchCandidate],
) -> list[DispatchCandidate]:
    """
    Score and rank candidates from strongest
    to weakest dispatch match.
    """

    scored_candidates = [
        calculate_candidate_score(candidate) for candidate in candidates
    ]

    return sorted(
        scored_candidates,
        key=lambda candidate: (
            candidate.score,
            -candidate.distance_km,
            candidate.rating,
        ),
        reverse=True,
    )


def select_best_candidate(
    candidates: list[DispatchCandidate],
) -> DispatchCandidate | None:
    """
    Return the highest-ranked eligible driver.

    Return None when no candidate receives
    a positive dispatch score.
    """

    ranked_candidates = rank_candidates(candidates)

    if not ranked_candidates:
        return None

    best_candidate = ranked_candidates[0]

    if best_candidate.score <= 0:
        return None

    return best_candidate
