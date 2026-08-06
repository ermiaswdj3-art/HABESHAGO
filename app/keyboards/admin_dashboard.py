from telegram import (
    KeyboardButton,
)

from app.state.user_context import (
    get_user_context,
)

from app.keyboards.workspace_layout import (
    build_workspace,
)


def get_admin_dashboard_keyboard(
    user_id,
):
    """
    Return the HABESHAGO
    Operations Center.
    """

    context = get_user_context(
        user_id
    )

    header = [
        [
            KeyboardButton(
                "🩺 System Health"
            ),
            KeyboardButton(
                "📊 Live Statistics"
            ),
        ]
    ]

    primary = [
        [
            KeyboardButton(
                "👥 Manage Drivers"
            ),
            KeyboardButton(
                "📋 Active Ride Queue"
            ),
        ],
        [
            KeyboardButton(
                "🔄 Recover Active Rides"
            ),
        ],
    ]

    secondary = []

    if context[
        "has_active_driver_ride"
    ]:
        secondary.append(
            [
                KeyboardButton(
                    "🚖 Resume Active Ride"
                )
            ]
        )

    secondary.append(
        [
            KeyboardButton(
                "🚖 Driver Dashboard"
            ),
            KeyboardButton(
                "👤 My Profile"
            ),
        ]
    )

    footer = [
        [
            KeyboardButton(
                "🏠 Main Menu"
            ),
        ]
    ]

    return build_workspace(
        header_buttons=header,
        primary_buttons=primary,
        secondary_buttons=secondary,
        footer_buttons=footer,
    )