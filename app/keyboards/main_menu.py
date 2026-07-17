from telegram import ReplyKeyboardMarkup


def get_main_menu():
    keyboard = [
        ["🛺 Request Ride"],
        ["📍 Ride Status", "📋 My Rides"],
        ["📦 Send Package"],
        ["💼 Become a Driver"],
        ["👤 My Profile"],
        ["☎️ Contact Support"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )