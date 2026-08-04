"""
HABESHAGO Driver Registration Entry Handler

Starts the canonical Driver Registration Wizard only
when the Telegram user does not already have a driver
application or approved driver profile.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.contact import (
    get_contact_keyboard,
)

from app.keyboards.driver_dashboard import (
    get_driver_dashboard_keyboard,
)

from app.services.driver_registration_service import (
    get_driver_registration_status,
)

from app.state.driver_registration_state import (
    driver_registration_state,
)


async def become_driver(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Start the Driver Registration Wizard.

    Existing applicants and approved drivers are routed
    to their current registration status instead of
    creating duplicate registration attempts.
    """

    if update.message is None:
        return

    user_id = update.effective_user.id

    registration_status = (
        get_driver_registration_status(
            user_id
        )
    )

    if registration_status is not None:
        registration = registration_status[
            "registration"
        ]

        verification = registration_status[
            "verification"
        ]

        guidance = registration_status[
            "guidance"
        ]

        if registration_status["can_operate"]:
            await update.message.reply_text(
                "✅ Your HABESHAGO driver account "
                "is already approved.\n\n"
                "Your Driver Dashboard is ready.",
                reply_markup=(
                    get_driver_dashboard_keyboard()
                ),
            )
            return

        rejection_reason = registration.get(
            "rejection_reason"
        )

        rejection_section = ""

        if rejection_reason:
            rejection_section = (
                "\n\nReason\n"
                f"{rejection_reason}"
            )

        await update.message.reply_text(
            "🚖 HABESHAGO DRIVER APPLICATION\n\n"

            "Registration Status\n"
            f"{registration['label']}\n\n"

            "Identity Verification\n"
            f"{verification['identity'].replace('_', ' ').title()}\n\n"

            "Vehicle Verification\n"
            f"{verification['vehicle'].replace('_', ' ').title()}\n\n"

            f"{guidance['message']}\n\n"

            "Next Action\n"
            f"{guidance['next_action']}"

            f"{rejection_section}"
        )
        return

    # Clear any incomplete local wizard state before
    # beginning a fresh registration session.
    driver_registration_state[
        user_id
    ] = {
        "step": "phone_number",
    }

    await update.message.reply_text(
        "🚖 Welcome to HABESHAGO Driver Registration!\n\n"
        "We will collect your contact and vehicle "
        "information for verification.\n\n"
        "Completing this form submits an application. "
        "It does not activate the driver account "
        "immediately.\n\n"
        "📱 Tap the button below to securely share "
        "your phone number.",
        reply_markup=get_contact_keyboard(),
    )