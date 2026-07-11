from telegram import ReplyKeyboardMarkup


def get_tracking_menu():
    """
    Keyboard for drivers to share live location.
    """

    keyboard = [
        [
            "📡 Share Live Location",
        ],
        [
            "📍 Arrived",
        ],
        [
            "🚕 Start Trip",
        ],
        [
            "🏁 Complete Ride",
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )