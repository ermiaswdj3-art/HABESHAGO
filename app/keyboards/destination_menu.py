from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_destination_menu():
    """
    Destination selection menu.
    """

    keyboard = [
        [
            KeyboardButton(
                "🔍 Search Destination"
            ),
            KeyboardButton(
                "🕒 Recent Places"
            ),
        ],
        [
            KeyboardButton(
                "📍 Share Destination Location",
                request_location=True,
            ),
        ],
        [
            KeyboardButton(
                "❌ Cancel"
            ),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )