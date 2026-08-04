"""
HABESHAGO Fuel Vehicle Brand Keyboard

Builds the available fuel-car brands directly from the
canonical Vehicle Catalog.
"""

from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.data.vehicle_catalog import (
    VEHICLE_CATALOG,
)


def get_vehicle_brand_keyboard():
    """
    Return every supported fuel-car brand.
    """

    brands = list(
        VEHICLE_CATALOG[
            "Fuel Car"
        ].keys()
    )

    keyboard = []
    row = []

    for brand in brands:
        row.append(
            KeyboardButton(
                f"🚗 {brand}"
            )
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