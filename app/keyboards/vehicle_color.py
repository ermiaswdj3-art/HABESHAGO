from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_vehicle_color_keyboard():
    keyboard = [
        [
            KeyboardButton("⚪ White"),
            KeyboardButton("⚫ Black"),
        ],
        [
            KeyboardButton("🔘 Silver"),
            KeyboardButton("⚙️ Gray"),
        ],
        [
            KeyboardButton("🔵 Blue"),
            KeyboardButton("🔴 Red"),
        ],
        [
            KeyboardButton("🟢 Green"),
            KeyboardButton("🟡 Yellow"),
        ],
        [
            KeyboardButton("🟤 Brown"),
            KeyboardButton("🟣 Purple"),
        ],
        [
            KeyboardButton("🟠 Orange"),
            KeyboardButton("🚗 Other"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )