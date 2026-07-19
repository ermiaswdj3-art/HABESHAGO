from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def build_google_maps_url(
    latitude,
    longitude,
):
    """
    Build a Google Maps navigation URL
    for the supplied destination coordinates.
    """

    return (
        "https://www.google.com/maps/dir/"
        f"?api=1&destination={latitude},{longitude}"
    )


def get_pickup_navigation_keyboard(
    latitude,
    longitude,
):
    """
    Return an inline button that opens
    navigation to the passenger's pickup point.
    """

    maps_url = build_google_maps_url(
        latitude,
        longitude,
    )

    keyboard = [
        [
            InlineKeyboardButton(
                text="🧭 Navigate to Pickup",
                url=maps_url,
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_destination_navigation_keyboard(
    latitude,
    longitude,
):
    """
    Return an inline button that opens
    navigation to the ride destination.
    """

    maps_url = build_google_maps_url(
        latitude,
        longitude,
    )

    keyboard = [
        [
            InlineKeyboardButton(
                text="🏁 Navigate to Destination",
                url=maps_url,
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)