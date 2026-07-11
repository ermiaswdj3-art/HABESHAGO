import asyncio


async def send_driver_progress(context, passenger_id):
    """
    Simulate driver progress updates.
    """

    await asyncio.sleep(10)

    await context.bot.send_message(
        chat_id=passenger_id,
        text=(
            "🚗 Your driver is getting closer.\n\n"
            "⏱ Updated ETA: 3 minutes."
        ),
    )