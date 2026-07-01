from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_location_keyboard(button_text):
    keyboard = [
        [
            KeyboardButton(
                button_text,
                request_location=True,
            )
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )