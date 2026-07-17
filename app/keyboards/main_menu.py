from telegram import ReplyKeyboardMarkup


def get_main_menu():
    """
    HABESHAGO home screen shown to new passengers.
    """

    keyboard = [
        [
            "🛺 Request Ride",
            "💼 Register as Driver",
        ],
        [
            "🛵 Delivery",
            "☎️ Contact Support",
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )