import logging

from telegram import Update
from telegram.error import (
    BadRequest,
    Forbidden,
    NetworkError,
    RetryAfter,
    TimedOut,
)
from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)


async def global_error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handle unexpected HABESHAGO errors safely.

    Network interruptions are logged as warnings.
    Telegram request problems are classified.
    Unexpected application errors are logged with
    their complete traceback for debugging.
    """

    error = context.error

    # ==========================================
    # TELEGRAM CONNECTION TIMEOUT
    # ==========================================

    if isinstance(error, TimedOut):
        logger.warning(
            "Telegram request timed out. "
            "The action may be retried safely."
        )
        return

    # ==========================================
    # GENERAL NETWORK FAILURE
    # ==========================================

    if isinstance(error, NetworkError):
        logger.warning(
            "Telegram network error: %s",
            error,
        )
        return

    # ==========================================
    # TELEGRAM RATE LIMIT
    # ==========================================

    if isinstance(error, RetryAfter):
        logger.warning(
            "Telegram rate limit reached. "
            "Retry after %s seconds.",
            error.retry_after,
        )
        return

    # ==========================================
    # BOT BLOCKED OR CHAT UNAVAILABLE
    # ==========================================

    if isinstance(error, Forbidden):
        logger.warning(
            "Telegram access was forbidden. "
            "The user may have blocked the bot "
            "or the chat is unavailable: %s",
            error,
        )
        return

    # ==========================================
    # INVALID TELEGRAM REQUEST
    # ==========================================

    if isinstance(error, BadRequest):
        logger.warning(
            "Telegram rejected a request: %s",
            error,
        )
        return

    # ==========================================
    # UNEXPECTED APPLICATION ERROR
    # ==========================================

    logger.error(
        "Unexpected HABESHAGO error while "
        "processing an update.",
        exc_info=(
            type(error),
            error,
            error.__traceback__,
        ),
    )

    # Send a safe response when the failed update
    # contains a normal Telegram message.
    if (
        isinstance(update, Update)
        and update.effective_message is not None
    ):
        try:
            await update.effective_message.reply_text(
                "⚠️ HABESHAGO encountered a temporary "
                "problem while processing your request.\n\n"
                "Please try again."
            )

        except Exception:
            # Do not allow an error-response failure
            # to create another unhandled exception.
            logger.warning(
                "HABESHAGO could not send the "
                "fallback error message."
            )