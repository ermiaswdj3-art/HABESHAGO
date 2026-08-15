"""
HABESHAGO Authenticated Driver Mini App Launcher

Launches the Driver Mini App from an inline Telegram
Web App button so Telegram provides authenticated
Mini App initialization data to the driver client.
"""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    WebAppInfo,
)

from telegram.ext import ContextTypes

from app.config.settings import (
    HABESHAGO_MINI_APP_URL,
)


async def launch_driver_mini_app(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Present the authenticated Driver Mini App launcher.
    """

    if update.message is None:
        return

    base_url = (
        HABESHAGO_MINI_APP_URL
        or ""
    ).strip().rstrip("/")

    if not base_url:
        await update.message.reply_text(
            "Driver Mini App is currently unavailable."
        )
        return

    if not base_url.startswith("https://"):
        await update.message.reply_text(
            "Driver Mini App configuration is invalid."
        )
        return

    driver_url = (
        base_url
        + "/driver"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "\U0001F696 Launch Driver App",
                    web_app=WebAppInfo(
                        url=driver_url,
                    ),
                )
            ]
        ]
    )

    await update.message.reply_text(
        "\U0001F696 HABESHAGO DRIVER APP\n\n"
        "Open your authenticated Driver Mini App.",
        reply_markup=keyboard,
    )