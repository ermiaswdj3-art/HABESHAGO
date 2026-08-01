"""
HABESHAGO Decision Service

Generates, compares, and ranks mobility options for an
active passenger trip.

The current version uses controlled demonstration estimates.
Future versions can receive estimates from routing, traffic,
driver availability, transit schedules, weather, pricing,
and user-preference services.
"""

from typing import Any

from app.mini_app.models import Trip


def _build_base_options() -> list[dict[str, Any]]:
    """
    Build the available mobility options before ranking.
    """

    return [
        {
            "id": "ride",
            "title": "Ride",
            "icon": "\U0001F696",
            "description": "Fast private transportation.",
            "eta_minutes": 12,
            "price_etb": 210,
            "emissions_rank": 3,
        },
        {
            "id": "transit",
            "title": "Transit",
            "icon": "\U0001F68C",
            "description": "Affordable public transport.",
            "eta_minutes": 32,
            "price_etb": 35,
            "emissions_rank": 2,
        },
        {
            "id": "walk_transit",
            "title": "Walk + Transit",
            "icon": "\U0001F6B6",
            "description": (
                "Walk to the nearest stop, then continue by bus."
            ),
            "eta_minutes": 28,
            "price_etb": 25,
            "emissions_rank": 1,
        },
    ]


def _find_option(
    options: list[dict[str, Any]],
    option_id: str,
) -> dict[str, Any] | None:
    """
    Return an option by its unique identifier.
    """

    for option in options:
        if option["id"] == option_id:
            return option

    return None


def _apply_rankings(
    options: list[dict[str, Any]],
) -> None:
    """
    Calculate fastest, cheapest, greenest, and recommended
    option labels.
    """

    if not options:
        return

    fastest_option = min(
        options,
        key=lambda option: option["eta_minutes"],
    )

    cheapest_option = min(
        options,
        key=lambda option: option["price_etb"],
    )

    greenest_option = min(
        options,
        key=lambda option: option["emissions_rank"],
    )

    recommended_option = fastest_option

    ride_option = _find_option(options, "ride")

    for option in options:
        option["is_fastest"] = (
            option["id"] == fastest_option["id"]
        )

        option["is_cheapest"] = (
            option["id"] == cheapest_option["id"]
        )

        option["is_greenest"] = (
            option["id"] == greenest_option["id"]
        )

        option["is_recommended"] = (
            option["id"] == recommended_option["id"]
        )

        option["badge"] = ""
        option["recommendation_reason"] = ""

        if option["is_recommended"]:
            option["badge"] = "\u2B50 Recommended"
            option["recommendation_reason"] = (
                f"Fastest option at "
                f"{option['eta_minutes']} minutes."
            )

        elif option["is_cheapest"]:
            option["badge"] = "\U0001F4B0 Cheapest"

            if ride_option:
                savings = (
                    ride_option["price_etb"]
                    - option["price_etb"]
                )

                option["recommendation_reason"] = (
                    f"Save {savings} ETB compared with Ride."
                )
            else:
                option["recommendation_reason"] = (
                    "Lowest estimated price."
                )

        elif option["is_greenest"]:
            option["badge"] = (
                "\U0001F331 Lowest Emissions"
            )

            option["recommendation_reason"] = (
                "Lowest estimated environmental impact."
            )

        else:
            option["badge"] = "\u26A1 Fast Option"
            option["recommendation_reason"] = (
                "Balanced travel time and cost."
            )


def _prepare_display_values(
    options: list[dict[str, Any]],
) -> None:
    """
    Create display-ready labels for the Mini App UI.
    """

    for option in options:
        option["eta"] = (
            f"{option['eta_minutes']} min"
        )

        option["price"] = (
            f"{option['price_etb']} ETB"
        )


def generate_mobility_options(
    trip: Trip,
) -> list[dict[str, Any]]:
    """
    Generate ranked mobility options for an active trip.

    Returns an empty list when the trip is incomplete.
    """

    if not trip.is_ready_for_planning():
        return []

    options = _build_base_options()

    _apply_rankings(options)
    _prepare_display_values(options)

    return options