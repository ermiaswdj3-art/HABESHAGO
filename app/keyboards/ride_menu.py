from telegram import ReplyKeyboardMarkup


def get_ride_menu():
    keyboard = [
        ["🏁 Complete Ride"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )