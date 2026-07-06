from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_driver_location_keyboard():
    keyboard = [
        [
            KeyboardButton(
                text="📍 Share Current Location",
                request_location=True,
            )
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )