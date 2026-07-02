from telegram import ReplyKeyboardMarkup


def get_confirmation_keyboard():
    keyboard = [
        ["✅ Confirm Ride"],
        ["❌ Cancel Ride"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )