from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.data.vehicle_catalog import VEHICLE_CATALOG


def get_vehicle_model_keyboard(vehicle_type, brand):
    """
    Creates a keyboard containing every model
    for the selected vehicle brand.
    """

    models = VEHICLE_CATALOG[vehicle_type][brand]

    keyboard = []

    row = []

    for model in models:

        row.append(
            KeyboardButton(model)
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )