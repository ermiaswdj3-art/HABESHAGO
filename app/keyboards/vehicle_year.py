from telegram import KeyboardButton, ReplyKeyboardMarkup
from datetime import datetime


def get_vehicle_year_keyboard():
    """
    Creates a keyboard containing vehicle years
    from the current year back to 1990.
    """

    current_year = datetime.now().year

    keyboard = []

    row = []

    for year in range(current_year, 1989, -1):

        row.append(
            KeyboardButton(str(year))
        )

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )