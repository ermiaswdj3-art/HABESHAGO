"""
HABESHAGO Driver Dashboard Keyboard

Provides the canonical Telegram Driver Workspace.

The Mini App entry is intentionally a normal Telegram
text action. The authenticated Web App is launched by
the bot through a dedicated inline Web App button.
"""

from telegram import KeyboardButton

from app.keyboards.workspace_layout import (
    build_workspace,
)


def get_driver_dashboard_keyboard():
    """
    Return the canonical HABESHAGO Driver Workspace.

    Business state remains canonical and shared across
    Telegram Bot, Mini App, and future HABESHAGO clients.
    """

    header = [
        [
            KeyboardButton(
                "\U0001F696 Driver Dashboard"
            ),
        ],
    ]

    primary = [
        [
            KeyboardButton(
                "\U0001F310 Open HABESHAGO"
            ),
        ],
        [
            KeyboardButton(
                "\U0001F7E2 Go Online"
            ),
            KeyboardButton(
                "\U0001F534 Go Offline"
            ),
        ],
        [
            KeyboardButton(
                "\U0001F4CD Update My Location"
            ),
        ],
    ]

    secondary = [
        [
            KeyboardButton(
                "\U0001F464 My Profile"
            ),
            KeyboardButton(
                "\U0001F4CB My Rides"
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
