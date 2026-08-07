"""
HABESHAGO Notification Constants

Defines the canonical notification vocabulary used across
the shared HABESHAGO Notification Platform.
"""


class NotificationRecipient:
    # ==========================================
    # PLATFORM RECIPIENT TYPES
    # ==========================================

    PASSENGER = "PASSENGER"

    DRIVER = "DRIVER"

    ADMIN = "ADMIN"

    OPERATIONS = "OPERATIONS"


class NotificationChannel:
    # ==========================================
    # CURRENT CHANNELS
    # ==========================================

    TELEGRAM = "TELEGRAM"

    # ==========================================
    # FUTURE CHANNELS
    # ==========================================

    PUSH = "PUSH"

    SMS = "SMS"

    EMAIL = "EMAIL"


class NotificationCategory:
    # ==========================================
    # DRIVER ADMINISTRATION
    # ==========================================

    DRIVER_ADMINISTRATION = (
        "DRIVER_ADMINISTRATION"
    )


class NotificationPriority:
    NORMAL = "NORMAL"

    HIGH = "HIGH"

    CRITICAL = "CRITICAL"


class NotificationStatus:
    PENDING = "PENDING"

    DELIVERED = "DELIVERED"

    FAILED = "FAILED"