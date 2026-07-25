from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.state.user_context import (
    get_user_context,
)


def get_admin_dashboard_keyboard(
    user_id,
):
    """
    Return a context-aware HABESHAGO
    administrator operations keyboard.

    The Resume Active Ride button appears
    only when the administrator currently
    has an active driver ride.
    """

    user_context = get_user_context(
        user_id
    )

    keyboard = [
        [
            KeyboardButton(
                "🩺 System Health"
            ),
            KeyboardButton(
                "📊 Live Statistics"
            ),
        ],
        [
            KeyboardButton(
                "🔄 Recover Active Rides"
            ),
            KeyboardButton(
                "📋 Active Ride Queue"
            ),
        ],
    ]

    if user_context[
        "has_active_driver_ride"
    ]:
        keyboard.append(
            [
                KeyboardButton(
                    "🚖 Resume Active Ride"
                )
            ]
        )

    keyboard.extend(
        [
            [
                KeyboardButton(
                    "🚖 Driver Dashboard"
                ),
                KeyboardButton(
                    "👤 My Profile"
                ),
            ],
            [
                KeyboardButton(
                    "🏠 Main Menu"
                ),
            ],
        ]
    )

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )