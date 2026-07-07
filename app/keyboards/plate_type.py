from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_plate_type_keyboard():
    keyboard = [
        [
            KeyboardButton("🟦 Regional Plate"),
        ],
        [
            KeyboardButton("🟩 National ETH Plate"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )