"""
HABESHAGO Payment Page

Displays the final fare breakdown and available
payment methods after trip completion.
"""

from app.mini_app.context import get_trip
from app.mini_app.pages.app_shell import get_app_shell


def get_payment_page():
    """
    Build the HABESHAGO Payment page.
    """

    page = get_app_shell("home")

    trip = get_trip()

    page["title"] = "Complete Payment"

    page["subtitle"] = (
        "Review your final fare and choose a payment method."
    )

    page["trip"] = trip

    page["payment_methods"] = [
        {
            "id": "cash",
            "title": "Cash",
            "description": "Pay the driver directly.",
            "icon": "💵",
        },
        {
            "id": "telebirr",
            "title": "Telebirr",
            "description": "Pay using your Telebirr account.",
            "icon": "📱",
        },
        {
            "id": "cbe_birr",
            "title": "CBE Birr",
            "description": "Pay using CBE Birr.",
            "icon": "🏦",
        },
        {
            "id": "chapa",
            "title": "Chapa",
            "description": "Pay through Chapa.",
            "icon": "💳",
        },
        {
            "id": "arifpay",
            "title": "ArifPay",
            "description": "Pay through ArifPay.",
            "icon": "🌐",
        },
    ]

    return page