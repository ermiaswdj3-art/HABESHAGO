"""
HABESHAGO Dispatch Reasons

Defines the official decision reasons used by
the Intelligent Dispatch Platform.

Every dispatch decision should explain why
a driver was selected.
"""


class DispatchReason:
    # ==========================================
    # DISTANCE
    # ==========================================

    NEAREST_DRIVER = "NEAREST_DRIVER"

    # ==========================================
    # AVAILABILITY
    # ==========================================

    AVAILABLE_DRIVER = "AVAILABLE_DRIVER"

    # ==========================================
    # DRIVER QUALITY
    # ==========================================

    RATING_SCORE_APPLIED = "RATING_SCORE_APPLIED"

    # ==========================================
    # PLATFORM DECISION
    # ==========================================

    BEST_MATCH = "BEST_MATCH"
