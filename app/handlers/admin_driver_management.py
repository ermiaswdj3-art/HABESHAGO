"""
HABESHAGO Telegram Admin Driver Management Handler

Displays canonical driver-management information from the
shared Driver Management Platform.

This handler prepares governed administration workflows.
Actual business rules and persistent state transitions
remain owned by the shared Driver Administration Service.
"""

import logging

from telegram import Update
from telegram.error import (
    BadRequest,
    Forbidden,
    NetworkError,
    RetryAfter,
    TimedOut,
)
from telegram.ext import ContextTypes

from app.config.settings import (
    ADMIN_ID,
)

from app.keyboards.admin_driver_management import (
    get_admin_driver_confirmation_keyboard,
    get_admin_driver_list_keyboard,
    get_admin_driver_profile_keyboard,
    get_admin_driver_reason_cancel_keyboard,
)

from app.services.driver_administration_service import (
    approve_driver,
    reject_driver,
    resubmit_driver,
    restore_driver,
    suspend_driver,
)

from app.services.driver_management_service import (
    get_driver_management_dashboard,
    list_driver_management_dashboard,
)

from app.state.admin_driver_action_state import (
    STAGE_AWAITING_CONFIRMATION,
    STAGE_AWAITING_REASON,
    clear_pending_driver_admin_action,
    get_pending_driver_admin_action,
    is_awaiting_driver_admin_reason,
    set_pending_driver_admin_action,
    update_pending_driver_admin_reason,
)


logger = logging.getLogger(__name__)


REASON_REQUIRED_ACTIONS = {
    "REJECT",
    "SUSPEND",
}

CONFIRMATION_ONLY_ACTIONS = {
    "APPROVE",
    "RESTORE",
    "RESUBMIT",
}

SUPPORTED_DRIVER_ADMIN_ACTIONS = (
    REASON_REQUIRED_ACTIONS
    | CONFIRMATION_ONLY_ACTIONS
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


def _normalize_admin_action(
    action: str,
) -> str:
    """
    Normalize and validate one requested administration
    action.
    """

    normalized_action = str(
        action or ""
    ).strip().upper()

    if (
        normalized_action
        not in SUPPORTED_DRIVER_ADMIN_ACTIONS
    ):
        raise ValueError(
            "Unsupported driver administration action."
        )

    return normalized_action


def _load_actionable_dashboard(
    *,
    driver_id: int,
    action: str,
) -> dict:
    """
    Reload the canonical dashboard and ensure the requested
    action is still legal.

    This protects the workflow from stale inline buttons.
    """

    dashboard = (
        get_driver_management_dashboard(
            driver_id
        )
    )

    if dashboard is None:
        raise ValueError(
            "Driver profile could not be found."
        )

    if (
        action
        not in dashboard["available_actions"]
    ):
        raise ValueError(
            "This administrative action is no longer "
            "available for the driver."
        )

    return dashboard


def _execute_driver_admin_action(
    *,
    driver_id: int,
    actor_id: int,
    action: str,
    reason: str | None,
) -> dict:
    """
    Execute one confirmed action through the shared
    Driver Administration Service.

    This handler-level router contains no transition rules.
    Each canonical service function performs final
    validation and atomic persistence.
    """

    if action == "APPROVE":
        return approve_driver(
            driver_id=driver_id,
            actor_id=actor_id,
            reason=reason,
        )

    if action == "REJECT":
        if not reason:
            raise ValueError(
                "A rejection reason is required."
            )

        return reject_driver(
            driver_id=driver_id,
            actor_id=actor_id,
            reason=reason,
        )

    if action == "SUSPEND":
        if not reason:
            raise ValueError(
                "A suspension reason is required."
            )

        return suspend_driver(
            driver_id=driver_id,
            actor_id=actor_id,
            reason=reason,
        )

    if action == "RESTORE":
        return restore_driver(
            driver_id=driver_id,
            actor_id=actor_id,
            reason=reason,
        )

    if action == "RESUBMIT":
        return resubmit_driver(
            driver_id=driver_id,
            actor_id=actor_id,
            reason=reason,
        )

    raise ValueError(
        "Unsupported driver administration action."
    )


def _build_driver_notification_text(
    *,
    action: str,
    result: dict,
) -> str:
    """
    Build the driver-facing notification for a completed
    administrative action.
    """

    driver = result["driver"]

    registration_status = driver[
        "registration_status"
    ]

    reason = result["action"].get(
        "reason"
    )

    reason_text = (
        f"\n\nReason:\n{reason}"
        if reason
        else ""
    )

    action_messages = {
        "APPROVE": (
            "✅ Your HABESHAGO driver registration "
            "has been approved.\n\n"
            "You may now open your Driver Dashboard "
            "and choose when to go online."
        ),
        "REJECT": (
            "❌ Your HABESHAGO driver application "
            "has been rejected."
        ),
        "SUSPEND": (
            "⛔ Your HABESHAGO driver account "
            "has been suspended.\n\n"
            "You have been placed offline and cannot "
            "receive new ride offers."
        ),
        "RESTORE": (
            "♻️ Your HABESHAGO driver account "
            "has been restored.\n\n"
            "Your account remains offline until you "
            "voluntarily go online."
        ),
        "RESUBMIT": (
            "🔄 Your HABESHAGO driver application "
            "has been returned to verification.\n\n"
            "Your identity and vehicle records are "
            "waiting for a new review."
        ),
    }

    message = action_messages.get(
        action,
        "Your HABESHAGO driver registration "
        "status has been updated.",
    )

    return (
        f"{message}\n\n"
        "Current Registration Status: "
        f"{registration_status}"
        f"{reason_text}"
    )


async def _notify_driver_of_admin_action(
    *,
    context: ContextTypes.DEFAULT_TYPE,
    driver_id: int,
    action: str,
    result: dict,
) -> bool:
    """
    Notify the affected driver after a successful database
    transition.

    Notification failure never rolls back or invalidates
    the completed administrative action.
    """

    try:
        await context.bot.send_message(
            chat_id=driver_id,
            text=(
                _build_driver_notification_text(
                    action=action,
                    result=result,
                )
            ),
        )

        return True

    except (
        BadRequest,
        Forbidden,
        NetworkError,
        RetryAfter,
        TimedOut,
    ) as error:
        logger.warning(
            (
                "Driver administration action %s "
                "succeeded, but notification to "
                "driver %s failed: %s"
            ),
            action,
            driver_id,
            error,
        )

        return False


def _build_admin_action_success_text(
    *,
    action: str,
    result: dict,
    notification_sent: bool,
) -> str:
    """
    Build the administrator-facing completion message.
    """

    driver = result["driver"]
    audit_action = result["action"]

    notification_status = (
        "Sent successfully"
        if notification_sent
        else "Could not be delivered"
    )

    return (
        "✅ DRIVER ADMINISTRATION ACTION COMPLETED\n\n"

        f"Action: {_format_action_label(action)}\n"
        f"Driver ID: {driver['driver_id']}\n"
        f"Driver: {driver['full_name']}\n"
        "Registration Status: "
        f"{driver['registration_status']}\n"
        "Operational Status: "
        f"{driver['operational_status']}\n"
        "Action Reference: "
        f"{audit_action['action_reference']}\n"
        "Driver Notification: "
        f"{notification_status}\n\n"

        "The driver profile and durable audit history "
        "have been updated."
    )


def _build_action_confirmation_text(
    *,
    dashboard: dict,
    action: str,
    reason: str | None,
) -> str:
    """
    Build the final confirmation message for one prepared
    driver administration action.
    """

    profile = dashboard["profile"]
    registration = dashboard[
        "registration"
    ]
    operations = dashboard["operations"]

    reason_text = (
        reason
        if reason
        else "No reason supplied."
    )

    return (
        "⚠️ CONFIRM DRIVER ADMINISTRATION ACTION\n\n"

        f"Action: {_format_action_label(action)}\n"
        f"Driver ID: {dashboard['driver_id']}\n"
        f"Driver: {profile['full_name']}\n"
        "Current Registration Status: "
        f"{registration['status']}\n"
        "Current Operational Status: "
        f"{operations['status']}\n"
        f"Reason: {reason_text}\n\n"

        "The driver's canonical state will be reloaded "
        "again before execution.\n\n"

        "Confirm this administrative action?"
    )


def _build_reason_request_text(
    *,
    dashboard: dict,
    action: str,
) -> str:
    """
    Build the reason-entry prompt for rejection or
    suspension.
    """

    profile = dashboard["profile"]

    return (
        "📝 ADMINISTRATION REASON REQUIRED\n\n"

        f"Action: {_format_action_label(action)}\n"
        f"Driver: {profile['full_name']}\n"
        f"Driver ID: {dashboard['driver_id']}\n\n"

        "Send the reason as your next text message.\n\n"

        "The action will not be executed until you "
        "review and confirm it."
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
    registration = dashboard[
        "registration"
    ]
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
        "Verified At: "
        f"{registration['verified_at'] or 'Not verified'}\n"
        f"Rejection Reason: {rejection_text}\n\n"

        "OPERATIONS\n"
        f"Status: {operations['status']}\n"
        f"Online: {operations['is_online']}\n"
        f"Available: {operations['is_available']}\n"
        f"Active Ride: {operations['has_active_ride']}\n"
        "Active Ride ID: "
        f"{operations['active_ride_id'] or 'None'}\n\n"

        "ACTIVE VEHICLE\n"
        f"{vehicle_text}\n\n"

        "RIDE AND FINANCIAL ACTIVITY\n"
        f"Total Rides: {activity['total_rides']}\n"
        "Completed Rides: "
        f"{activity['completed_rides']}\n"
        "Cancelled Rides: "
        f"{activity['cancelled_rides']}\n"
        "Settled Rides: "
        f"{activity['settled_rides']}\n"
        "Unsettled Completed Rides: "
        f"{activity['unsettled_completed_rides']}\n"
        "Gross Fares: "
        f"{activity['gross_fares']:,.2f} ETB\n"
        "Commission: "
        f"{activity['commission']:,.2f} ETB\n"
        "Driver Earnings: "
        f"{activity['driver_earnings']:,.2f} ETB\n\n"

        "AVAILABLE ADMIN ACTIONS\n"
        f"{actions_text}\n\n"

        "ADMINISTRATION HISTORY\n"
        "Recorded Actions: "
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

    clear_pending_driver_admin_action(
        context.user_data
    )

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


async def handle_admin_driver_action_reason(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Capture a required rejection or suspension reason and
    advance the workflow to final confirmation.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if not _is_authorized_admin(
        user_id
    ):
        return

    if not is_awaiting_driver_admin_reason(
        context.user_data
    ):
        return

    reason = str(
        update.message.text or ""
    ).strip()

    try:
        pending_action = (
            update_pending_driver_admin_reason(
                context.user_data,
                reason,
            )
        )

        driver_id = int(
            pending_action["driver_id"]
        )

        action = _normalize_admin_action(
            pending_action["action"]
        )

        dashboard = (
            _load_actionable_dashboard(
                driver_id=driver_id,
                action=action,
            )
        )

    except (TypeError, ValueError) as error:
        clear_pending_driver_admin_action(
            context.user_data
        )

        await update.message.reply_text(
            "❌ The administration reason could not "
            "be accepted.\n\n"
            f"{error}"
        )
        return

    await update.message.reply_text(
        _build_action_confirmation_text(
            dashboard=dashboard,
            action=action,
            reason=(
                pending_action["reason"]
            ),
        ),
        reply_markup=(
            get_admin_driver_confirmation_keyboard(
                driver_id=driver_id,
                action=action,
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

    callback_data = query.data or ""

    # ==========================================
    # DRIVER LIST
    # ==========================================

    if callback_data == "admin_driver:list":
        await query.answer()

        clear_pending_driver_admin_action(
            context.user_data
        )

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

    # ==========================================
    # PREPARE ADMINISTRATION ACTION
    # ==========================================

    if callback_data.startswith(
        "admin_driver:action:"
    ):
        await query.answer()

        clear_pending_driver_admin_action(
            context.user_data
        )

        parts = callback_data.split(
            ":"
        )

        if len(parts) != 4:
            await query.edit_message_text(
                "❌ Invalid driver administration action."
            )
            return

        raw_action = parts[2]
        raw_driver_id = parts[3]

        try:
            action = _normalize_admin_action(
                raw_action
            )

            driver_id = int(
                raw_driver_id
            )

            dashboard = (
                _load_actionable_dashboard(
                    driver_id=driver_id,
                    action=action,
                )
            )

        except (TypeError, ValueError) as error:
            clear_pending_driver_admin_action(
                context.user_data
            )

            await query.edit_message_text(
                "❌ The administrative action could not "
                "be prepared.\n\n"
                f"{error}"
            )
            return

        if action in REASON_REQUIRED_ACTIONS:
            set_pending_driver_admin_action(
                context.user_data,
                driver_id=driver_id,
                action=action,
                stage=(
                    STAGE_AWAITING_REASON
                ),
            )

            await query.edit_message_text(
                _build_reason_request_text(
                    dashboard=dashboard,
                    action=action,
                ),
                reply_markup=(
                    get_admin_driver_reason_cancel_keyboard(
                        driver_id
                    )
                ),
            )
            return

        set_pending_driver_admin_action(
            context.user_data,
            driver_id=driver_id,
            action=action,
            stage=(
                STAGE_AWAITING_CONFIRMATION
            ),
        )

        await query.edit_message_text(
            _build_action_confirmation_text(
                dashboard=dashboard,
                action=action,
                reason=None,
            ),
            reply_markup=(
                get_admin_driver_confirmation_keyboard(
                    driver_id=driver_id,
                    action=action,
                )
            ),
        )
        return

    # ==========================================
    # CANCEL ADMINISTRATION ACTION
    # ==========================================

    if callback_data.startswith(
        "admin_driver:cancel:"
    ):
        await query.answer(
            "Administrative action cancelled."
        )

        raw_driver_id = callback_data.rsplit(
            ":",
            1,
        )[-1]

        clear_pending_driver_admin_action(
            context.user_data
        )

        try:
            driver_id = int(
                raw_driver_id
            )

        except ValueError:
            await query.edit_message_text(
                "✅ Administrative action cancelled."
            )
            return

        dashboard = (
            get_driver_management_dashboard(
                driver_id
            )
        )

        if dashboard is None:
            await query.edit_message_text(
                "✅ Administrative action cancelled."
            )
            return

        await query.edit_message_text(
            "✅ Administrative action cancelled.\n\n"
            + _build_driver_profile_text(
                dashboard
            ),
            reply_markup=(
                get_admin_driver_profile_keyboard(
                    driver_id,
                    dashboard[
                        "available_actions"
                    ],
                )
            ),
        )
        return

    # ==========================================
    # CONFIRM ADMINISTRATION ACTION
    # ==========================================

    if callback_data.startswith(
        "admin_driver:confirm:"
    ):
        pending_action = (
            get_pending_driver_admin_action(
                context.user_data
            )
        )

        if pending_action is None:
            await query.answer(
                "This workflow has expired.",
                show_alert=True,
            )

            await query.edit_message_text(
                "❌ This administrative workflow has "
                "expired.\n\n"
                "Open the driver profile and begin again."
            )
            return

        parts = callback_data.split(
            ":"
        )

        if len(parts) != 4:
            clear_pending_driver_admin_action(
                context.user_data
            )

            await query.answer(
                "Invalid confirmation.",
                show_alert=True,
            )
            return

        try:
            callback_action = (
                _normalize_admin_action(
                    parts[2]
                )
            )

            callback_driver_id = int(
                parts[3]
            )

            pending_driver_id = int(
                pending_action["driver_id"]
            )

            pending_action_name = (
                _normalize_admin_action(
                    pending_action["action"]
                )
            )

        except (TypeError, ValueError):
            clear_pending_driver_admin_action(
                context.user_data
            )

            await query.answer(
                "Invalid confirmation.",
                show_alert=True,
            )
            return

        if (
            callback_driver_id
            != pending_driver_id
            or callback_action
            != pending_action_name
            or pending_action.get("stage")
            != STAGE_AWAITING_CONFIRMATION
        ):
            clear_pending_driver_admin_action(
                context.user_data
            )

            await query.answer(
                "This confirmation does not match "
                "the pending workflow.",
                show_alert=True,
            )
            return

        try:
            _load_actionable_dashboard(
                driver_id=callback_driver_id,
                action=callback_action,
            )

        except ValueError as error:
            clear_pending_driver_admin_action(
                context.user_data
            )

            await query.answer(
                "The driver state has changed.",
                show_alert=True,
            )

            await query.edit_message_text(
                "❌ The administrative action is no "
                "longer available.\n\n"
                f"{error}"
            )
            return

        reason = pending_action.get(
            "reason"
        )

        try:
            result = (
                _execute_driver_admin_action(
                    driver_id=(
                        callback_driver_id
                    ),
                    actor_id=user_id,
                    action=callback_action,
                    reason=reason,
                )
            )

        except ValueError as error:
            clear_pending_driver_admin_action(
                context.user_data
            )

            await query.answer(
                "The administrative action failed.",
                show_alert=True,
            )

            dashboard = (
                get_driver_management_dashboard(
                    callback_driver_id
                )
            )

            if dashboard is None:
                await query.edit_message_text(
                    "❌ The administrative action "
                    "could not be completed.\n\n"
                    f"{error}"
                )
                return

            await query.edit_message_text(
                "❌ The administrative action "
                "could not be completed.\n\n"
                f"{error}\n\n"
                + _build_driver_profile_text(
                    dashboard
                ),
                reply_markup=(
                    get_admin_driver_profile_keyboard(
                        callback_driver_id,
                        dashboard[
                            "available_actions"
                        ],
                    )
                ),
            )
            return

        clear_pending_driver_admin_action(
            context.user_data
        )

        notification_sent = (
            await _notify_driver_of_admin_action(
                context=context,
                driver_id=callback_driver_id,
                action=callback_action,
                result=result,
            )
        )

        updated_dashboard = (
            get_driver_management_dashboard(
                callback_driver_id
            )
        )

        await query.answer(
            "Driver administration action completed."
        )

        if updated_dashboard is None:
            await query.edit_message_text(
                _build_admin_action_success_text(
                    action=callback_action,
                    result=result,
                    notification_sent=(
                        notification_sent
                    ),
                )
            )
            return

        await query.edit_message_text(
            _build_admin_action_success_text(
                action=callback_action,
                result=result,
                notification_sent=(
                    notification_sent
                ),
            )
            + "\n\n"
            + _build_driver_profile_text(
                updated_dashboard
            ),
            reply_markup=(
                get_admin_driver_profile_keyboard(
                    callback_driver_id,
                    updated_dashboard[
                        "available_actions"
                    ],
                )
            ),
        )
        return

    # ==========================================
    # VIEW DRIVER PROFILE
    # ==========================================

    if callback_data.startswith(
        "admin_driver:view:"
    ):
        await query.answer()

        clear_pending_driver_admin_action(
            context.user_data
        )

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
                    driver_id,
                    dashboard[
                        "available_actions"
                    ],
                )
            ),
        )
        return

    # ==========================================
    # UNKNOWN DRIVER CALLBACK
    # ==========================================

    await query.answer(
        "Unknown Driver Management action.",
        show_alert=True,
    )