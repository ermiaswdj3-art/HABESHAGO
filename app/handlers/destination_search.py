import asyncio

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from app.services.destination_search_service import (
    search_destinations,
)

from app.keyboards.confirmation import (
    get_confirmation_keyboard,
)

from app.services.distance_service import (
    calculate_distance,
)

from app.services.pricing_service import (
    calculate_fare,
)

from app.state.destination_search_state import (
    destination_search_state,
)

from app.state.ride_state import (
    ride_requests,
)


async def start_destination_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Put the passenger into destination-search mode.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if (
        user_id not in ride_requests
        or ride_requests[user_id].get("status")
        != "waiting_for_destination"
    ):
        await update.message.reply_text(
            "❌ Please share your pickup location first."
        )
        return

    destination_search_state[user_id] = True

    await update.message.reply_text(
        "🔍 Type the destination name.\n\n"
        "Examples:\n"
        "• Bole\n"
        "• Meskel Square\n"
        "• Piassa\n"
        "• Ayat\n"
        "• CMC"
    )


async def handle_destination_query(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Search OpenStreetMap using the passenger's
    typed destination query.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    if not destination_search_state.get(user_id):
        return

    query = update.message.text.strip()

    if len(query) < 2:
        await update.message.reply_text(
            "❌ Please type at least 2 characters."
        )
        return

    await update.message.reply_text(
        f"🔍 Searching for: {query}..."
    )

    results = await asyncio.to_thread(
        search_destinations,
        query,
        "en",
    )

    if not results:
        await update.message.reply_text(
            "😔 No matching destinations were found.\n\n"
            "Please try another place name."
        )
        return

    context.user_data["destination_results"] = results

    keyboard = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{index}. 📍 {result['name']}",
                    callback_data=f"destination:{index - 1}",
                )
            ]
        )

    await update.message.reply_text(
        "📍 I found these places.\n\n"
        "Please choose your destination:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def select_destination(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Save the destination selected from
    the inline search results.
    """

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    user_id = query.from_user.id

    if user_id not in ride_requests:
        await query.edit_message_text(
            "❌ Your ride request has expired.\n\n"
            "Please request a new ride."
        )
        return

    callback_data = query.data or ""

    try:
        result_index = int(
            callback_data.split(":")[1]
        )
    except (
        IndexError,
        TypeError,
        ValueError,
    ):
        await query.edit_message_text(
            "❌ Invalid destination selection."
        )
        return

    results = context.user_data.get(
        "destination_results",
        [],
    )

    if not 0 <= result_index < len(results):
        await query.edit_message_text(
            "❌ That destination is no longer available.\n\n"
            "Please search again."
        )
        return

    selected = results[result_index]

    destination = (
        selected["latitude"],
        selected["longitude"],
    )

    ride_requests[user_id]["destination"] = destination
    ride_requests[user_id]["destination_name"] = selected["name"]
    ride_requests[user_id]["status"] = "completed"

    destination_search_state.pop(
        user_id,
        None,
    )

    context.user_data.pop(
        "destination_results",
        None,
    )

    pickup = ride_requests[user_id]["pickup"]

    distance = calculate_distance(
        pickup[0],
        pickup[1],
        destination[0],
        destination[1],
    )

    fare = calculate_fare(distance)

    await query.edit_message_text(
        "✅ Destination selected!\n\n"
        f"🏁 {selected['name']}"
    )

    if query.message is None:
        return

    await query.message.reply_text(
        "🚖 Ride Summary\n\n"
        f"🏁 Destination: {selected['name']}\n"
        f"📏 Estimated Distance: {distance:.2f} km\n"
        f"💰 Estimated Fare: {fare:.2f} ETB\n\n"
        "Would you like to confirm this ride?",
        reply_markup=get_confirmation_keyboard(),
    )   