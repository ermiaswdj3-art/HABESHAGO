"""
HABESHAGO Electric Vehicle Brand Keyboard

Builds the available electric-car brands directly from the
canonical Vehicle Catalog.
"""

from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.data.vehicle_catalog import (
    VEHICLE_CATALOG,
)


def get_electric_vehicle_brand_keyboard():
    """
    Return every supported electric-car brand.
    """

    brands = list(
        VEHICLE_CATALOG[
            "Electric Car"
        ].keys()
    )

    keyboard = []
    row = []

    for brand in brands:
        icon = (
            "🚗"
            if brand == "Other"
            else "⚡"
        )

        row.append(
            KeyboardButton(
                f"{icon} {brand}"
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