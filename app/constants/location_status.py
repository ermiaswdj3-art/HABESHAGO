"""
HABESHAGO Location Status

Defines the official status values used
by the Live Location Platform.

These values describe how trustworthy
a driver's latest location is.
"""


class LocationStatus:
    # ==========================================
    # LOCATION QUALITY
    # ==========================================

    LIVE = "LIVE"

    STALE = "STALE"

    UNKNOWN = "UNKNOWN"

    # ==========================================
    # DRIVER STATE
    # ==========================================

    MOVING = "MOVING"

    STOPPED = "STOPPED"
