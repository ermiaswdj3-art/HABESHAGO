from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_electric_vehicle_brand_keyboard():
    keyboard = [
        [
            KeyboardButton("⚡ BYD"),
            KeyboardButton("⚡ Tesla"),
        ],
        [
            KeyboardButton("⚡ GAC AION"),
            KeyboardButton("⚡ Changan"),
        ],
        [
            KeyboardButton("⚡ Hyundai"),
            KeyboardButton("⚡ Kia"),
        ],
        [
            KeyboardButton("⚡ Volkswagen"),
            KeyboardButton("🚗 Other"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )