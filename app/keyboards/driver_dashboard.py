from telegram import (
    KeyboardButton,
)

from app.keyboards.workspace_layout import (
    build_workspace,
)


def get_driver_dashboard_keyboard():
    """
    Return the HABESHAGO Driver Workspace.

    Built using the shared Workspace Builder
    so every HABESHAGO workspace follows
    the same design language.
    """

    header = [
        [
            KeyboardButton(
                "🚖 Driver Dashboard"
            ),
        ],
    ]

    primary = [
        [
            KeyboardButton(
                "🟢 Go Online"
            ),
            KeyboardButton(
                "🔴 Go Offline"
            ),
        ],
    ]

    secondary = [
        [
            KeyboardButton(
                "👤 My Profile"
            ),
            KeyboardButton(
                "📋 My Rides"
            ),
        ],
    ]

    footer = []

    return build_workspace(
        header_buttons=header,
        primary_buttons=primary,
        secondary_buttons=secondary,
        footer_buttons=footer,
    )