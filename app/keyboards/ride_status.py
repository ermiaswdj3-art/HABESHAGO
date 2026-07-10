from telegram import ReplyKeyboardMarkup


def get_ride_status_keyboard():
    keyboard = [
        ["📍 Ride Status"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )