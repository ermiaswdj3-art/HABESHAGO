"""
HABESHAGO Official Ride State Contract

These constants define the platform-wide ride
lifecycle vocabulary.

Important:
Some canonical state names intentionally retain
legacy database values so HABESHAGO can migrate
incrementally without breaking existing rides.
"""


class RideState:
    """
    Official HABESHAGO ride lifecycle states.
    """

    # ==========================================
    # REQUEST AND DRIVER SEARCH
    # ==========================================

    REQUESTED = "REQUESTED"

    SEARCHING_DRIVER = "SEARCHING_DRIVER"

    DRIVER_ASSIGNED = "DRIVER_ASSIGNED"

    # Canonical name:
    # DRIVER_ACCEPTED
    #
    # Existing HABESHAGO database value:
    # ACCEPTED
    DRIVER_ACCEPTED = "ACCEPTED"

    # Canonical name:
    # DRIVER_EN_ROUTE
    #
    # Existing HABESHAGO database value:
    # DRIVER_ARRIVING
    DRIVER_EN_ROUTE = "DRIVER_ARRIVING"

    # ==========================================
    # PICKUP AND TRIP
    # ==========================================

    DRIVER_ARRIVED = "DRIVER_ARRIVED"

    PASSENGER_ON_BOARD = "PASSENGER_ON_BOARD"

    TRIP_STARTED = "TRIP_STARTED"

    TRIP_COMPLETED = "TRIP_COMPLETED"

    # ==========================================
    # TERMINAL STATES
    # ==========================================

    RATED = "RATED"

    CANCELLED = "CANCELLED"

    EXPIRED = "EXPIRED"

    ARCHIVED = "ARCHIVED"

    # ==========================================
    # LEGACY COMPATIBILITY ALIASES
    # ==========================================

    ACCEPTED = DRIVER_ACCEPTED

    DRIVER_ARRIVING = DRIVER_EN_ROUTE