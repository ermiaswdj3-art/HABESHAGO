from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.confirmation import (
    get_confirmation_keyboard,
)

from app.services.distance_service import (
    calculate_distance,
)

from app.services.pricing_service import (
    calculate_fare,
)

from app.state.ride_state import (
    ride_requests,
)


async def select_recent_place(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Use a passenger's selected recent place
    as the destination for the current ride.
    """

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    user_id = query.from_user.id

    if (
        user_id not in ride_requests
        or ride_requests[user_id].get("status")
        != "waiting_for_destination"
    ):
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
            "❌ Invalid recent-place selection."
        )
        return

    recent_places = context.user_data.get(
        "recent_places",
        [],
    )

    if not 0 <= result_index < len(recent_places):
        await query.edit_message_text(
            "❌ That recent place is no longer available.\n\n"
            "Please open Recent Places again."
        )
        return

    place = recent_places[result_index]

    place_name = place[1]
    full_address = place[2]
    latitude = place[3]
    longitude = place[4]

    destination = (
        latitude,
        longitude,
    )

    ride_requests[user_id]["destination"] = destination
    ride_requests[user_id]["destination_name"] = place_name
    ride_requests[user_id]["destination_full_name"] = full_address
    ride_requests[user_id]["status"] = "completed"

    pickup = ride_requests[user_id]["pickup"]

    pickup_name = ride_requests[user_id].get(
        "pickup_name",
        "Pickup location",
    )

    distance = calculate_distance(
        pickup[0],
        pickup[1],
        destination[0],
        destination[1],
    )

    fare = calculate_fare(distance)

    context.user_data.pop(
        "recent_places",
        None,
    )

    await query.edit_message_text(
        "✅ Recent destination selected!\n\n"
        f"🏁 {place_name}"
    )

    if query.message is None:
        return

    await query.message.reply_text(
        "🚕 Ride Summary\n\n"
        "📍 From\n"
        f"{pickup_name}\n\n"
        "🏁 To\n"
        f"{place_name}\n\n"
        "📏 Distance\n"
        f"{distance:.2f} km\n\n"
        "💰 Estimated Fare\n"
        f"{fare:.2f} ETB\n\n"
        "Would you like to confirm this ride?",
        reply_markup=get_confirmation_keyboard(),
    )