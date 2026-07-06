from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_toyota_model_keyboard():
    keyboard = [
        [
            KeyboardButton("Vitz"),
            KeyboardButton("Corolla"),
        ],
        [
            KeyboardButton("Yaris"),
            KeyboardButton("Hilux"),
        ],
        [
            KeyboardButton("Land Cruiser"),
            KeyboardButton("RAV4"),
        ],
        [
            KeyboardButton("Prado"),
            KeyboardButton("Camry"),
        ],
        [
            KeyboardButton("Other"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )