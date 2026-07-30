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
    using fresh live-location data.

    Drivers without a fresh usable location
    are excluded from dispatch.

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

    driver_locations = {}

    # ==========================================
    # BUILD DISPATCH CANDIDATES
    # ==========================================

    for driver in drivers:
        driver_id = driver[0]

        print(
            "\nChecking dispatch candidate:",
            driver_id,
            driver[1],
        )

        # During controlled local testing, only
        # explicitly approved driver accounts are
        # considered. When no test IDs are set,
        # every eligible driver is considered.
        if test_driver_ids and driver_id not in test_driver_ids:
            print("Rejected: not included in " "HABESHAGO_TEST_DRIVER_IDS.")
            continue

        # The database coordinates are no longer
        # trusted for live dispatch decisions.
        live_location = get_usable_live_location(driver_id)

        print(
            "Usable live location:",
            live_location,
        )

        if live_location is None:
            print("Rejected: no fresh usable " "live location.")
            continue

        distance = calculate_distance(
            passenger_latitude,
            passenger_longitude,
            live_location.latitude,
            live_location.longitude,
        )

        print(
            "Calculated pickup distance:",
            f"{distance:.2f} km",
        )

        if distance > MAX_PICKUP_DISTANCE_KM:
            print("Rejected: outside maximum " "pickup distance.")
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

        driver_locations[driver_id] = live_location

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

    selected_location = driver_locations[best_candidate.driver_id]

    # ==========================================
    # DISPATCH DECISION LOG
    # ==========================================

    print("\n========== HABESHAGO DISPATCH ==========")

    print(
        "Driver ID:",
        selected_driver[0],
    )

    print(
        "Driver Name:",
        selected_driver[1],
    )

    print(
        "Pickup Distance:",
        f"{best_candidate.distance_km:.2f} km",
    )

    print(
        "Dispatch Score:",
        f"{best_candidate.score:.2f}",
    )

    print(
        "Dispatch Reasons:",
        best_candidate.reasons,
    )

    print(
        "Location Status:",
        selected_location.status,
    )

    print(
        "Location Recorded At:",
        selected_location.recorded_at,
    )

    print("========================================\n")

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
        "location_status": (selected_location.status),
        "location_recorded_at": (selected_location.recorded_at),
    }
