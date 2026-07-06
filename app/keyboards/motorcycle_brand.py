from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_motorcycle_brand_keyboard():
    keyboard = [
        [
            KeyboardButton("🏍 Bajaj"),
            KeyboardButton("🏍 TVS"),
        ],
        [
            KeyboardButton("🏍 Yamaha"),
            KeyboardButton("🏍 Honda"),
        ],
        [
            KeyboardButton("🏍 Suzuki"),
            KeyboardButton("🏍 Hero"),
        ],
        [
            KeyboardButton("🏍 KTM"),
            KeyboardButton("🏍 Royal Enfield"),
        ],
        [
            KeyboardButton("🏍 BMW"),
            KeyboardButton("🏍 Ducati"),
        ],
        [
            KeyboardButton("🏍 Kawasaki"),
            KeyboardButton("🏍 Harley-Davidson"),
        ],
        [
            KeyboardButton("🏍 Other"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )