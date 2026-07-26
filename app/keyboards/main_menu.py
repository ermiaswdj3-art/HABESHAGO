from telegram import (
    KeyboardButton,
)

from app.keyboards.workspace_layout import (
    build_workspace,
)


def get_main_menu():
    """
    Return the HABESHAGO Passenger Workspace.

    Built using the shared Workspace Builder
    so every HABESHAGO workspace follows
    the same design language.
    """

    header = []

    primary = [
        [
            KeyboardButton(
                "🛺 Request Ride"
            ),
            KeyboardButton(
                "💼 Register as Driver"
            ),
        ],
    ]

    secondary = [
        [
            KeyboardButton(
                "🛵 Delivery"
            ),
            KeyboardButton(
                "☎️ Contact Support"
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