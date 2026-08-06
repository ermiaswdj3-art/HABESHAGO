"""
HABESHAGO Telegram Admin Driver Management Handler

Displays canonical driver-management information from the
shared Driver Management Platform.

This handler does not calculate business values and does
not change driver state directly.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import (
    ADMIN_ID,
)

from app.keyboards.admin_driver_management import (
    get_admin_driver_list_keyboard,
    get_admin_driver_profile_keyboard,
)

from app.services.driver_management_service import (
    get_driver_management_dashboard,
    list_driver_management_dashboard,
)


def _is_authorized_admin(
    user_id: int,
) -> bool:
    """
    Return True only for the configured administrator.
    """

    return (
        ADMIN_ID is not None
        and str(user_id) == str(ADMIN_ID)
    )


def _format_action_label(
    action: str,
) -> str:
    """
    Return a readable administrative action label.
    """

    labels = {
        "APPROVE": "Approve Driver",
        "REJECT": "Reject Application",
        "SUSPEND": "Suspend Driver",
        "RESTORE": "Restore Driver",
        "RESUBMIT": "Return to Verification",
    }

    return labels.get(
        action,
        action.replace(
            "_",
            " ",
        ).title(),
    )


def _build_driver_list_text(
    drivers: list[dict],
) -> str:
    """
    Build the compact driver-list message.
    """

    if not drivers:
        return (
            "👥 HABESHAGO DRIVER MANAGEMENT\n\n"
            "No driver records were found."
        )

    approved = sum(
        1
        for driver in drivers
        if driver["registration_status"]
        == "approved"
    )

    pending = sum(
        1
        for driver in drivers
        if driver["registration_status"]
        == "verification_pending"
    )

    suspended = sum(
        1
        for driver in drivers
        if driver["registration_status"]
        == "suspended"
    )

    rejected = sum(
        1
        for driver in drivers
        if driver["registration_status"]
        == "rejected"
    )

    return (
        "👥 HABESHAGO DRIVER MANAGEMENT\n\n"
        "Shared Platform Driver Records\n\n"
        f"Total Drivers: {len(drivers)}\n"
        f"Approved: {approved}\n"
        f"Verification Pending: {pending}\n"
        f"Suspended: {suspended}\n"
        f"Rejected: {rejected}\n\n"
        "Select a driver to inspect the complete "
        "management profile."
    )


def _build_driver_profile_text(
    dashboard: dict,
) -> str:
    """
    Build the complete Telegram management profile.
    """

    profile = dashboard["profile"]
    registration = dashboard["registration"]
    operations = dashboard["operations"]
    vehicles = dashboard["vehicles"]
    activity = dashboard["activity"]

    active_vehicle = vehicles[
        "active_vehicle"
    ]

    if active_vehicle is None:
        vehicle_text = (
            "No active vehicle"
        )

    else:
        plate = active_vehicle["plate"]

        vehicle_text = (
            f"{active_vehicle['display_name']}\n"
            f"Color: {active_vehicle['color']}\n"
            f"Plate: {plate['number']}\n"
            "Verification: "
            f"{active_vehicle['verification_status']}"
        )

    available_actions = dashboard[
        "available_actions"
    ]

    if available_actions:
        action_lines = [
            (
                "• "
                + _format_action_label(
                    action
                )
            )
            for action in available_actions
        ]

        actions_text = "\n".join(
            action_lines
        )

    elif operations["has_active_ride"]:
        actions_text = (
            "No actions available while the "
            "driver has an active ride."
        )

    else:
        actions_text = (
            "No administrative actions are "
            "currently available."
        )

    rejection_reason = registration[
        "rejection_reason"
    ]

    rejection_text = (
        rejection_reason
        if rejection_reason
        else "None"
    )

    return (
        "👤 DRIVER MANAGEMENT PROFILE\n\n"

        f"Driver ID: {dashboard['driver_id']}\n"
        f"Name: {profile['full_name']}\n"
        f"Phone: "
        f"{profile['phone_number'] or 'Not provided'}\n"
        f"Rating: {profile['rating']:.2f}\n\n"

        "REGISTRATION\n"
        f"Status: {registration['status']}\n"
        "Identity Verification: "
        f"{registration['identity_verification_status']}\n"
        "Vehicle Verification: "
        f"{registration['vehicle_verification_status']}\n"
        f"Verified At: "
        f"{registration['verified_at'] or 'Not verified'}\n"
        f"Rejection Reason: {rejection_text}\n\n"

        "OPERATIONS\n"
        f"Status: {operations['status']}\n"
        f"Online: {operations['is_online']}\n"
        f"Available: {operations['is_available']}\n"
        f"Active Ride: {operations['has_active_ride']}\n"
        f"Active Ride ID: "
        f"{operations['active_ride_id'] or 'None'}\n\n"

        "ACTIVE VEHICLE\n"
        f"{vehicle_text}\n\n"

        "RIDE AND FINANCIAL ACTIVITY\n"
        f"Total Rides: {activity['total_rides']}\n"
        f"Completed Rides: "
        f"{activity['completed_rides']}\n"
        f"Cancelled Rides: "
        f"{activity['cancelled_rides']}\n"
        f"Settled Rides: "
        f"{activity['settled_rides']}\n"
        "Unsettled Completed Rides: "
        f"{activity['unsettled_completed_rides']}\n"
        f"Gross Fares: "
        f"{activity['gross_fares']:,.2f} ETB\n"
        f"Commission: "
        f"{activity['commission']:,.2f} ETB\n"
        f"Driver Earnings: "
        f"{activity['driver_earnings']:,.2f} ETB\n\n"

        "AVAILABLE ADMIN ACTIONS\n"
        f"{actions_text}\n\n"

        "ADMINISTRATION HISTORY\n"
        f"Recorded Actions: "
        f"{dashboard['administration_action_count']}"
    )


async def show_admin_driver_management(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Display the canonical list of managed drivers.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if not _is_authorized_admin(
        user_id
    ):
        await update.message.reply_text(
            "❌ Administrator access required."
        )
        return

    drivers = (
        list_driver_management_dashboard()
    )

    await update.message.reply_text(
        _build_driver_list_text(
            drivers
        ),
        reply_markup=(
            get_admin_driver_list_keyboard(
                drivers
            )
        ),
    )


async def route_admin_driver_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Route Driver Management inline callbacks.
    """

    query = update.callback_query

    if query is None:
        return

    user_id = update.effective_user.id

    if not _is_authorized_admin(
        user_id
    ):
        await query.answer(
            "Administrator access required.",
            show_alert=True,
        )
        return

    await query.answer()

    callback_data = query.data or ""

    if callback_data == "admin_driver:list":
        drivers = (
            list_driver_management_dashboard()
        )

        await query.edit_message_text(
            _build_driver_list_text(
                drivers
            ),
            reply_markup=(
                get_admin_driver_list_keyboard(
                    drivers
                )
            ),
        )
        return

    if callback_data.startswith(
        "admin_driver:view:"
    ):
        raw_driver_id = callback_data.rsplit(
            ":",
            1,
        )[-1]

        try:
            driver_id = int(
                raw_driver_id
            )

        except ValueError:
            await query.edit_message_text(
                "❌ Invalid driver identifier."
            )
            return

        dashboard = (
            get_driver_management_dashboard(
                driver_id
            )
        )

        if dashboard is None:
            await query.edit_message_text(
                "❌ Driver profile could not be found."
            )
            return

        await query.edit_message_text(
            _build_driver_profile_text(
                dashboard
            ),
            reply_markup=(
                get_admin_driver_profile_keyboard(
                    driver_id
                )
            ),
        )