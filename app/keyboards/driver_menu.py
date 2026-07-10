from telegram import ReplyKeyboardMarkup


def get_driver_menu():
    keyboard = [
        ["🚖 Driver Dashboard"],
        ["🟢 Go Online", "🔴 Go Offline"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )