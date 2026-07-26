from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def build_workspace(
    header_buttons,
    primary_buttons,
    secondary_buttons=None,
    footer_buttons=None,
):
    """
    Build a HABESHAGO workspace using a
    consistent layout shared by every role.

    Layout:

    Header
    Primary actions
    Secondary actions
    Footer
    """

    keyboard = []

    if header_buttons:
        keyboard.extend(header_buttons)

    if primary_buttons:
        keyboard.extend(primary_buttons)

    if secondary_buttons:
        keyboard.extend(secondary_buttons)

    if footer_buttons:
        keyboard.extend(footer_buttons)

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )