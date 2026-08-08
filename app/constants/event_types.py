"""
HABESHAGO Event Types

This module defines the official event
vocabulary used across the HABESHAGO
platform.

Every significant business action should
eventually publish one of these events.

The Event Engine becomes the central
communication layer between platform
components.
"""


class EventType:
    # ==========================================
    # RIDE EVENTS
    # ==========================================

    RIDE_REQUESTED = "RIDE_REQUESTED"

    DRIVER_ASSIGNED = "DRIVER_ASSIGNED"

    DRIVER_ACCEPTED = "DRIVER_ACCEPTED"

    DRIVER_ARRIVED = "DRIVER_ARRIVED"

    PASSENGER_ON_BOARD = "PASSENGER_ON_BOARD"

    TRIP_STARTED = "TRIP_STARTED"

    TRIP_COMPLETED = "TRIP_COMPLETED"

    RIDE_CANCELLED = "RIDE_CANCELLED"

    # ==========================================
    # DRIVER EVENTS
    # ==========================================

    DRIVER_ONLINE = "DRIVER_ONLINE"

    DRIVER_OFFLINE = "DRIVER_OFFLINE"

    # ==========================================
    # DRIVER ADMINISTRATION EVENTS
    # ==========================================

    DRIVER_APPROVED = "DRIVER_APPROVED"

    DRIVER_REJECTED = "DRIVER_REJECTED"

    DRIVER_SUSPENDED = "DRIVER_SUSPENDED"

    DRIVER_RESTORED = "DRIVER_RESTORED"

    DRIVER_RESUBMITTED = "DRIVER_RESUBMITTED"

    # ==========================================
    # PASSENGER EVENTS
    # ==========================================

    PASSENGER_REGISTERED = "PASSENGER_REGISTERED"

    DRIVER_REGISTERED = "DRIVER_REGISTERED"

    # ==========================================
    # PRICING EVENTS
    # ==========================================

    PRICING_QUOTE_ISSUED = (
        "PRICING_QUOTE_ISSUED"
    )

    PRICING_ADJUSTED = (
        "PRICING_ADJUSTED"
    )

    FINANCIAL_ALLOCATION_CREATED = (
        "FINANCIAL_ALLOCATION_CREATED"
    )

    # ==========================================
    # PLATFORM EVENTS
    # ==========================================

    STATE_CHANGED = "STATE_CHANGED"
