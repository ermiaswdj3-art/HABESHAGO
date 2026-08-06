"""
HABESHAGO Driver Administration Actions

Defines the official administrative actions that may
change a driver's registration and operating permission.
"""


class DriverAdminAction:
    """
    Canonical Driver Administration action vocabulary.
    """

    APPROVE = "APPROVE"

    REJECT = "REJECT"

    SUSPEND = "SUSPEND"

    RESTORE = "RESTORE"

    RESUBMIT = "RESUBMIT"


DRIVER_ADMIN_ACTIONS = {
    DriverAdminAction.APPROVE,
    DriverAdminAction.REJECT,
    DriverAdminAction.SUSPEND,
    DriverAdminAction.RESTORE,
    DriverAdminAction.RESUBMIT,
}