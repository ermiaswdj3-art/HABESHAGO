from telegram import ReplyKeyboardMarkup


def get_availability_keyboard():
    keyboard = [
        [
            "🟢 Go Online",
            "🔴 Go Offline",
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )