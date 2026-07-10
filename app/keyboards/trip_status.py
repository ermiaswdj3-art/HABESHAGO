from telegram import ReplyKeyboardMarkup


def get_trip_status_keyboard():
    keyboard = [
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