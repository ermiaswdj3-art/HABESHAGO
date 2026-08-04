"""
HABESHAGO Motorcycle Brand Keyboard

Builds the available motorcycle brands directly from the
canonical Vehicle Catalog.
"""

from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.data.vehicle_catalog import (
    VEHICLE_CATALOG,
)


def get_motorcycle_brand_keyboard():
    """
    Return every supported motorcycle brand.
    """

    brands = list(
        VEHICLE_CATALOG[
            "Motorcycle"
        ].keys()
    )

    keyboard = []
    row = []

    for brand in brands:
        row.append(
            KeyboardButton(
                f"🏍 {brand}"
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