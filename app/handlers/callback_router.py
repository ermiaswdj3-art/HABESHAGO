from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.destination_search import (
    select_destination,
)

from app.handlers.recent_place_selection import (
    select_recent_place,
)

async def route_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Central router for all inline button callbacks.
    """

    query = update.callback_query

    if query is None:
        return

    callback_data = query.data or ""

    # ==========================================
    # DESTINATION SEARCH
    # ==========================================

    if callback_data.startswith(
        "destination:"
    ):
        await select_destination(
            update,
            context,
        )
        return

    # ==========================================
    # RECENT PLACES
    # ==========================================
    if callback_data.startswith(
        "recent_place:"
    ):
        await select_recent_place(
            update,
            context,
        )
        return

    # ==========================================
    # FUTURE CALLBACKS
    # ==========================================

    if callback_data.startswith(
        "favorite:"
    ):
        return

    if callback_data == "home":
        return

    if callback_data == "work":
        return