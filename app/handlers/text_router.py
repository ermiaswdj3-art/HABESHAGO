from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.destination_search import (
    handle_destination_query,
)

from app.handlers.driver_registration import (
    driver_registration_handler,
)

from app.state.destination_search_state import (
    destination_search_state,
)


async def route_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Route ordinary text to the correct active workflow.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    # Passenger is currently searching for a destination.
    if destination_search_state.get(user_id):
        await handle_destination_query(
            update,
            context,
        )
        return

    # Otherwise, allow the driver-registration
    # workflow to process the text when applicable.
    await driver_registration_handler(
        update,
        context,
    )