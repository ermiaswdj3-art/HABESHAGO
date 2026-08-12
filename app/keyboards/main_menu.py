from telegram import (
    KeyboardButton,
    WebAppInfo,
)

from app.config.settings import (
    HABESHAGO_MINI_APP_URL,
)

from app.keyboards.workspace_layout import (
    build_workspace,
)


def get_main_menu():
    """
    Return the HABESHAGO Passenger Workspace.

    When the Mini App URL is configured, expose a
    Telegram Web App launcher directly inside the
    passenger workspace.

    When the Mini App URL is unavailable, preserve the
    existing Telegram passenger experience unchanged.
    """

    header = []

    primary = []

    if HABESHAGO_MINI_APP_URL:
        primary.append(
            [
                KeyboardButton(
                    "🌐 Open HABESHAGO",
                    web_app=WebAppInfo(
                        url=HABESHAGO_MINI_APP_URL
                    ),
                ),
            ]
        )

    primary.append(
        [
            KeyboardButton(
                "🛺 Request Ride"
            ),
            KeyboardButton(
                "💼 Register as Driver"
            ),
        ]
    )

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