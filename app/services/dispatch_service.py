"""
HABESHAGO Intelligent Dispatch Service

Coordinates real driver data with the
Intelligent Dispatch Engine.

Responsibilities:
- Load eligible drivers
- Calculate pickup distance
- Build dispatch candidates
- Apply pickup-radius rules
- Apply an optional development-driver filter
- Rank candidates
- Return the strongest driver match
"""

import os

from app.database.driver_repository import (
    get_available_drivers,
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
            test_driver_ids.add(int(cleaned_value))

        except ValueError:
            continue

    return test_driver_ids


def find_best_driver(
    passenger_latitude: float,
    passenger_longitude: float,
) -> dict | None:
    """
    Find the strongest eligible driver match
    for the passenger's pickup location.

    Return None when no suitable driver exists.
    """

    # ==========================================
    # LOAD ELIGIBLE DRIVERS
    # ==========================================

    drivers = get_available_drivers()

    if not drivers:
        return None

    test_driver_ids = _get_test_driver_ids()

    candidates: list[DispatchCandidate] = []

    driver_records: dict[
        int,
        tuple,
    ] = {}

    # ==========================================
    # BUILD DISPATCH CANDIDATES
    # ==========================================

    for driver in drivers:
        driver_id = driver[0]

        # During controlled local testing, only
        # explicitly approved driver accounts are
        # considered. With no environment value,
        # all eligible drivers are considered.
        if test_driver_ids and driver_id not in test_driver_ids:
            continue

        driver_latitude = driver[7]
        driver_longitude = driver[8]

        distance = calculate_distance(
            passenger_latitude,
            passenger_longitude,
            driver_latitude,
            driver_longitude,
        )

        if distance > MAX_PICKUP_DISTANCE_KM:
            continue

        candidate = DispatchCandidate(
            driver_id=driver_id,
            distance_km=distance,
            rating=float(driver[6]),
            is_online=True,
            is_available=True,
            has_active_ride=(driver_id in active_rides),
        )

        candidates.append(candidate)

        driver_records[driver_id] = driver

    if not candidates:
        return None

    # ==========================================
    # RANK CANDIDATES
    # ==========================================

    ranked_candidates = rank_candidates(candidates)

    eligible_candidates = [
        candidate for candidate in ranked_candidates if candidate.score > 0
    ]

    if not eligible_candidates:
        return None

    best_candidate = eligible_candidates[0]

    selected_driver = driver_records[best_candidate.driver_id]

    # ==========================================
    # RETURN COMPATIBLE DRIVER RESULT
    # ==========================================

    return {
        "telegram_id": selected_driver[0],
        "name": selected_driver[1],
        "phone": selected_driver[2],
        "vehicle": selected_driver[3],
        "color": selected_driver[4],
        "plate": selected_driver[5],
        "rating": selected_driver[6],
        "distance": round(
            best_candidate.distance_km,
            2,
        ),
        "dispatch_score": round(
            best_candidate.score,
            2,
        ),
        "dispatch_reasons": list(best_candidate.reasons),
    }
