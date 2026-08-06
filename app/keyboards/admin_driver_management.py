"""
HABESHAGO Admin Driver Management Keyboards

Builds administrator-facing inline navigation for the
shared Driver Management Platform.
"""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


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
                callback_data="admin_driver:list",
            )
        ]
    )

    return InlineKeyboardMarkup(
        keyboard
    )


def get_admin_driver_profile_keyboard(
    driver_id: int,
) -> InlineKeyboardMarkup:
    """
    Return navigation for one driver-management profile.

    Administrative write actions are intentionally not
    exposed until confirmation and reason collection are
    added to the Telegram workflow.
    """

    return InlineKeyboardMarkup(
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