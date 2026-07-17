from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_passenger_phone_keyboard():
    keyboard = [
        [
            KeyboardButton(
                "📱 Share Phone Number",
                request_contact=True,
            ),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )