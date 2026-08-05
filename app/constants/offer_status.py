"""
HABESHAGO Ride Offer Status Contract

Defines the canonical lifecycle vocabulary for driver
ride offers across every HABESHAGO client.
"""


PENDING = "PENDING"

ACCEPTED = "ACCEPTED"

REJECTED = "REJECTED"

EXPIRED = "EXPIRED"

CANCELLED = "CANCELLED"


TERMINAL_OFFER_STATUSES = {
    ACCEPTED,
    REJECTED,
    EXPIRED,
    CANCELLED,
}


ALL_OFFER_STATUSES = {
    PENDING,
    *TERMINAL_OFFER_STATUSES,
}