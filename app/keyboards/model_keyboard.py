"""
HABESHAGO Vehicle Model Keyboard

Builds vehicle-model options from the canonical
Vehicle Catalog.
"""

from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.data.vehicle_catalog import (
    VEHICLE_CATALOG,
)


def get_vehicle_model_keyboard(
    vehicle_type: str,
    brand: str,
):
    """
    Return supported models for one vehicle type and brand.

    Unknown combinations safely fall back to "Other"
    instead of raising a KeyError.
    """

    vehicle_catalog = (
        VEHICLE_CATALOG.get(
            vehicle_type,
            {},
        )
    )

    models = vehicle_catalog.get(
        brand,
        ["Other"],
    )

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