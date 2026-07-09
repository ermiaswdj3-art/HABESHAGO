from telegram import ReplyKeyboardMarkup


def get_driver_dashboard_keyboard():
    keyboard = [
        [
            "🚖 Driver Dashboard",
        ],
        [
            "🟢 Go Online",
            "🔴 Go Offline",
        ],
        [
            "👤 My Profile",
            "📋 My Rides",
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )