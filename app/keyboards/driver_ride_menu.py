from telegram import ReplyKeyboardMarkup


def get_driver_ride_menu():
    """
    Keyboard shown to drivers when a new ride request arrives.
    """

    keyboard = [
        ["✅ Accept Ride"],
        ["❌ Decline Ride"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )