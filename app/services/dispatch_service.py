"""
HABESHAGO Intelligent Dispatch Service

Coordinates real driver data with the
Intelligent Dispatch Engine.

Responsibilities:
- Load eligible drivers
- Require a fresh live driver location
- Calculate pickup distance
- Build dispatch candidates
- Apply pickup-radius rules
- Apply an optional development-driver filter
- Exclude drivers with pending ride offers
- Rank candidates
- Return canonical dispatch results
"""

import os

from app.database.driver_repository import (
    get_available_drivers,
)

from app.database.ride_offer_repository import (
    get_pending_offer_driver_ids,
)

from app.models.dispatch_candidate import (
    DispatchCandidate,
)

from app.services.dispatch_engine import (
    rank_candidates,
)

from app.services.distance_service import (
    calculate_distance,
)

from app.services.live_location_service import (
    get_usable_live_location,
)

from app.state.active_ride_state import (
    active_rides,
)


MAX_PICKUP_DISTANCE_KM = 10.0


def _get_test_driver_ids() -> set[int]:
    """
    Return driver IDs allowed during controlled
    development testing.

    When HABESHAGO_TEST_DRIVER_IDS is empty or
    missing, no development filter is applied.
    """

    raw_driver_ids = os.getenv(
        "HABESHAGO_TEST_DRIVER_IDS",
        "",
    ).strip()

    if not raw_driver_ids:
        return set()

    test_driver_ids: set[int] = set()

    for value in raw_driver_ids.split(","):
        cleaned_value = value.strip()

        if not cleaned_value:
            continue

        try:
            test_driver_ids.add(
                int(cleaned_value)
            )

        except ValueError:
            continue

    return test_driver_ids


def _serialize_ranked_candidate(
    candidate: DispatchCandidate,
    driver_record: tuple,
    live_location,
) -> dict:
    """
    Convert one ranked dispatch candidate into the
    canonical shared dispatch-result contract.
    """

    return {
        "telegram_id": driver_record[0],
        "name": driver_record[1],
        "phone": driver_record[2],
        "vehicle": driver_record[3],
        "color": driver_record[4],
        "plate": driver_record[5],
        "rating": float(
            driver_record[6] or 0
        ),
        "distance": round(
            candidate.distance_km,
            2,
        ),
        "dispatch_score": round(
            candidate.score,
            2,
        ),
        "dispatch_reasons": list(
            candidate.reasons
        ),
        "disqualification_reason": (
            candidate.disqualification_reason
        ),
        "location_status": (
            live_location.status
        ),
        "location_recorded_at": (
            live_location.recorded_at
        ),
    }


def find_ranked_drivers(
    passenger_latitude: float,
    passenger_longitude: float,
) -> list[dict]:
    """
    Return every eligible driver ranked from strongest
    to weakest dispatch match.

    This is the canonical shared ranking contract used by
    Telegram, the Mini App, future native apps, and Admin.
    """

    drivers = get_available_drivers()

    if not drivers:
        return []

    test_driver_ids = (
        _get_test_driver_ids()
    )

    pending_offer_driver_ids = (
        get_pending_offer_driver_ids()
    )

    candidates: list[
        DispatchCandidate
    ] = []

    driver_records: dict[
        int,
        tuple,
    ] = {}

    driver_locations = {}

    for driver in drivers:
        driver_id = driver[0]

        if (
            test_driver_ids
            and driver_id
            not in test_driver_ids
        ):
            continue

        live_location = (
            get_usable_live_location(
                driver_id
            )
        )

        if live_location is None:
            continue

        distance = calculate_distance(
            passenger_latitude,
            passenger_longitude,
            live_location.latitude,
            live_location.longitude,
        )

        if distance > MAX_PICKUP_DISTANCE_KM:
            continue

        candidate = DispatchCandidate(
            driver_id=driver_id,
            distance_km=distance,
            rating=float(
                driver[6] or 0
            ),
            is_online=True,
            is_available=True,
            has_active_ride=(
                driver_id in active_rides
            ),
            has_pending_offer=(
                driver_id
                in pending_offer_driver_ids
            ),
        )

        candidates.append(
            candidate
        )

        driver_records[
            driver_id
        ] = driver

        driver_locations[
            driver_id
        ] = live_location

    ranked_candidates = rank_candidates(
        candidates
    )

    ranked_results = []

    for candidate in ranked_candidates:
        if not candidate.is_eligible():
            continue

        if candidate.score <= 0:
            continue

        driver_record = driver_records[
            candidate.driver_id
        ]

        live_location = driver_locations[
            candidate.driver_id
        ]

        ranked_results.append(
            _serialize_ranked_candidate(
                candidate,
                driver_record,
                live_location,
            )
        )

    return ranked_results


def find_best_driver(
    passenger_latitude: float,
    passenger_longitude: float,
) -> dict | None:
    """
    Return the strongest eligible driver match.

    This compatibility function delegates to the
    canonical ranked-driver contract.
    """

    ranked_drivers = find_ranked_drivers(
        passenger_latitude,
        passenger_longitude,
    )

    if not ranked_drivers:
        return None

    return ranked_drivers[0]