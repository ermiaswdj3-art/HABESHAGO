"""
HABESHAGO Admin Driver Management Keyboards

Builds administrator-facing navigation and governed
administrative-action controls for the shared Driver
Management Platform.

Buttons expose only actions supplied by the canonical
Driver Management Service.
"""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


ACTION_LABELS = {
    "APPROVE": "✅ Approve Driver",
    "REJECT": "❌ Reject Application",
    "SUSPEND": "⛔ Suspend Driver",
    "RESTORE": "♻️ Restore Driver",
    "RESUBMIT": "🔄 Return to Verification",
}


def get_admin_driver_list_keyboard(
    drivers: list[dict],
) -> InlineKeyboardMarkup:
    """
    Return one selectable button for every managed driver.
    """

    keyboard = []

    for driver in drivers:
        status = driver[
            "registration_status"
        ]

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"{driver['full_name']} "
                        f"• {status}"
                    ),
                    callback_data=(
                        "admin_driver:view:"
                        f"{driver['driver_id']}"
                    ),
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔄 Refresh Drivers",
                callback_data=(
                    "admin_driver:list"
                ),
            )
        ]
    )

    return InlineKeyboardMarkup(
        keyboard
    )


def get_admin_driver_profile_keyboard(
    driver_id: int,
    available_actions: list[str],
) -> InlineKeyboardMarkup:
    """
    Return legal administration actions and navigation for
    one driver-management profile.
    """

    keyboard = []

    for action in available_actions:
        normalized_action = str(
            action
        ).strip().upper()

        label = ACTION_LABELS.get(
            normalized_action,
            normalized_action.replace(
                "_",
                " ",
            ).title(),
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=(
                        "admin_driver:action:"
                        f"{normalized_action}:"
                        f"{driver_id}"
                    ),
                )
            ]
        )

    keyboard.extend(
        [
            [
                InlineKeyboardButton(
                    text="🔄 Refresh Profile",
                    callback_data=(
                        "admin_driver:view:"
                        f"{driver_id}"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back to Drivers",
                    callback_data=(
                        "admin_driver:list"
                    ),
                )
            ],
        ]
    )

    return InlineKeyboardMarkup(
        keyboard
    )


def get_admin_driver_confirmation_keyboard(
    *,
    driver_id: int,
    action: str,
) -> InlineKeyboardMarkup:
    """
    Return confirmation and cancellation controls for one
    prepared administrative action.
    """

    normalized_action = str(
        action
    ).strip().upper()

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="✅ Confirm Action",
                    callback_data=(
                        "admin_driver:confirm:"
                        f"{normalized_action}:"
                        f"{driver_id}"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data=(
                        "admin_driver:cancel:"
                        f"{driver_id}"
                    ),
                )
            ],
        ]
    )


def get_admin_driver_reason_cancel_keyboard(
    driver_id: int,
) -> InlineKeyboardMarkup:
    """
    Return a cancellation button while the administrator is
    entering a rejection or suspension reason.
    """

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="❌ Cancel Action",
                    callback_data=(
                        "admin_driver:cancel:"
                        f"{driver_id}"
                    ),
                )
            ]
        ]
    )