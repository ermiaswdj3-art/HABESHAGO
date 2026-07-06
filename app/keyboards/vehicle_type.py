from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_vehicle_type_keyboard():
    keyboard = [
        [KeyboardButton("⛽ Fuel Car")],
        [KeyboardButton("⚡ Electric Car")],
        [KeyboardButton("🏍 Motorcycle")],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )