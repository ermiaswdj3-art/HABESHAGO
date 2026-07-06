from telegram import ReplyKeyboardMarkup


def get_vehicle_brand_keyboard():
    keyboard = [
        ["🚗 Toyota", "🚗 Hyundai"],
        ["🚗 Suzuki", "🚗 Kia"],
        ["🚗 Nissan", "🚗 Honda"],
        ["🚗 Other"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )