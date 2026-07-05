from telegram import Update
from telegram.ext import ContextTypes

from app.state.driver_state import pending_driver_requests


async def driver_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Temporary placeholder.
    We will implement this in the next step.
    """
    await update.message.reply_text(
        "✅ Ride accepted. (Implementation coming next.)"
    )


async def driver_decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Temporary placeholder.
    We will implement this in the next step.
    """
    await update.message.reply_text(
        "❌ Ride declined. (Implementation coming next.)"
    )