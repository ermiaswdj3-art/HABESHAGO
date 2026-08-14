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


def get_driver_dashboard_keyboard():
    """
    Return the HABESHAGO Driver Workspace.

    Built using the shared Workspace Builder
    so every HABESHAGO workspace follows
    the same design language.

    The Mini App launch button uses the same
    configured HABESHAGO Mini App URL as the
    passenger workspace. Driver identity and
    authority are resolved by the shared
    platform after the Mini App opens.
    """

    header = [
        [
            KeyboardButton(
                "🚖 Driver Dashboard"
            ),
        ],
    ]

    primary = []

    if HABESHAGO_MINI_APP_URL:
        primary.append(
            [
                KeyboardButton(
                    "🌐 Open HABESHAGO",
                    web_app=WebAppInfo(
                        url=(
                            HABESHAGO_MINI_APP_URL.rstrip("/")
                            + "/driver"
                        )
                    ),
                ),
            ]
        )

    primary.append(
        [
            KeyboardButton(
                "🟢 Go Online"
            ),
            KeyboardButton(
                "🔴 Go Offline"
            ),
        ]
    )

    primary.append(
        [
            KeyboardButton(
                "📍 Update My Location"
            ),
        ]
    )

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
