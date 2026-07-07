from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_plate_region_keyboard():

    keyboard = [

        [
            KeyboardButton("AA"),
            KeyboardButton("OR"),
            KeyboardButton("AM"),
        ],

        [
            KeyboardButton("AF"),
            KeyboardButton("SM"),
            KeyboardButton("GM"),
        ],

        [
            KeyboardButton("BG"),
            KeyboardButton("HR"),
            KeyboardButton("DD"),
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