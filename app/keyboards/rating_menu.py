from telegram import ReplyKeyboardMarkup


def get_rating_menu():
    keyboard = [
        ["⭐ 1", "⭐ 2", "⭐ 3"],
        ["⭐ 4", "⭐ 5"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )