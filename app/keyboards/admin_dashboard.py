from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_admin_dashboard_keyboard():
    """
    Return the HABESHAGO administrator
    operations keyboard.
    """

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

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )