"""
HABESHAGO Driver Management Service

Builds the canonical administrator-facing driver profile
shared by Telegram Admin, future Web Admin, native clients,
and authorized platform APIs.

This service prepares management information only.
Administrative state changes remain owned by the
Driver Administration Service.
"""

from app.database.database import (
    create_connection,
)

from app.services.driver_administration_service import (
    get_managed_driver,
    list_managed_drivers,
)

from app.services.driver_dashboard_service import (
    get_driver_dashboard,
)

from app.services.vehicle_management_service import (
    get_driver_vehicle_management,
)


def _get_driver_activity_summary(
    driver_id: int,
) -> dict:
    """
    Return canonical ride and settlement activity for one
    driver.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),

            SUM(
                CASE
                    WHEN status IN (
                        'TRIP_COMPLETED',
                        'RATED'
                    )
                        THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN status = 'CANCELLED'
                        THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN settlement_status = 'settled'
                         AND status IN (
                             'TRIP_COMPLETED',
                             'RATED'
                         )
                        THEN 1
                    ELSE 0
                END
            ),

            SUM(
                CASE
                    WHEN settlement_status = 'not_settled'
                         AND status IN (
                             'TRIP_COMPLETED',
                             'RATED'
                         )
                        THEN 1
                    ELSE 0
                END
            ),

            COALESCE(
                SUM(
                    CASE
                        WHEN settlement_status = 'settled'
                             AND status IN (
                                 'TRIP_COMPLETED',
                                 'RATED'
                             )
                            THEN fare
                        ELSE 0
                    END
                ),
                0
            ),

            COALESCE(
                SUM(
                    CASE
                        WHEN settlement_status = 'settled'
                             AND status IN (
                                 'TRIP_COMPLETED',
                                 'RATED'
                             )
                            THEN commission_amount
                        ELSE 0
                    END
                ),
                0
            ),

            COALESCE(
                SUM(
                    CASE
                        WHEN settlement_status = 'settled'
                             AND status IN (
                                 'TRIP_COMPLETED',
                                 'RATED'
                             )
                            THEN driver_earnings
                        ELSE 0
                    END
                ),
                0
            )

        FROM rides
        WHERE driver_id = ?
        """,
        (driver_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {
            "total_rides": 0,
            "completed_rides": 0,
            "cancelled_rides": 0,
            "settled_rides": 0,
            "unsettled_completed_rides": 0,
            "gross_fares": 0.0,
            "commission": 0.0,
            "driver_earnings": 0.0,
        }

    return {
        "total_rides": int(
            row[0] or 0
        ),
        "completed_rides": int(
            row[1] or 0
        ),
        "cancelled_rides": int(
            row[2] or 0
        ),
        "settled_rides": int(
            row[3] or 0
        ),
        "unsettled_completed_rides": int(
            row[4] or 0
        ),
        "gross_fares": float(
            row[5] or 0
        ),
        "commission": float(
            row[6] or 0
        ),
        "driver_earnings": float(
            row[7] or 0
        ),
    }


def _build_available_actions(
    managed_driver: dict,
) -> list[str]:
    """
    Return the legal administrative actions available for
    the driver's current state.
    """

    registration_status = (
        managed_driver[
            "registration_status"
        ]
    )

    if (
        registration_status
        == "verification_pending"
    ):
        return [
            "APPROVE",
            "REJECT",
        ]

    if registration_status == "approved":
        if managed_driver["has_active_ride"]:
            return []

        return [
            "SUSPEND",
        ]

    if registration_status == "suspended":
        return [
            "RESTORE",
        ]

    if registration_status == "rejected":
        return [
            "RESUBMIT",
        ]

    return []


def get_driver_management_dashboard(
    driver_id: int,
) -> dict | None:
    """
    Build one complete canonical Driver Management
    dashboard contract.
    """

    managed_driver = get_managed_driver(
        driver_id
    )

    if managed_driver is None:
        return None

    dashboard = get_driver_dashboard(
        driver_id
    )

    vehicles = (
        get_driver_vehicle_management(
            driver_id
        )
    )

    activity = (
        _get_driver_activity_summary(
            driver_id
        )
    )

    if dashboard is not None:
        profile = dashboard["profile"]

    else:
        profile = {
            "full_name": (
                managed_driver["full_name"]
            ),
            "phone_number": None,
            "rating": 0.0,
        }

    administration_history = (
        managed_driver[
            "administration_history"
        ]
    )

    return {
        "driver_id": (
            managed_driver["driver_id"]
        ),
        "profile": profile,
        "registration": {
            "status": (
                managed_driver[
                    "registration_status"
                ]
            ),
            "identity_verification_status": (
                managed_driver[
                    "identity_verification_status"
                ]
            ),
            "vehicle_verification_status": (
                managed_driver[
                    "vehicle_verification_status"
                ]
            ),
            "verified_at": (
                managed_driver["verified_at"]
            ),
            "rejection_reason": (
                managed_driver[
                    "rejection_reason"
                ]
            ),
        },
        "operations": {
            "status": (
                managed_driver[
                    "operational_status"
                ]
            ),
            "is_online": (
                managed_driver["is_online"]
            ),
            "is_available": (
                managed_driver[
                    "is_available"
                ]
            ),
            "has_active_ride": (
                managed_driver[
                    "has_active_ride"
                ]
            ),
            "active_ride_id": (
                managed_driver[
                    "active_ride_id"
                ]
            ),
        },
        "vehicles": vehicles,
        "activity": activity,
        "available_actions": (
            _build_available_actions(
                managed_driver
            )
        ),
        "administration_history": (
            administration_history
        ),
        "administration_action_count": len(
            administration_history
        ),
    }


def list_driver_management_dashboard(
    *,
    registration_status: str | None = None,
    operational_status: str | None = None,
) -> list[dict]:
    """
    Return compact administrator-facing driver summaries.
    """

    managed_drivers = (
        list_managed_drivers(
            registration_status=(
                registration_status
            ),
            operational_status=(
                operational_status
            ),
        )
    )

    summaries = []

    for driver in managed_drivers:
        summaries.append(
            {
                "driver_id": (
                    driver["driver_id"]
                ),
                "full_name": (
                    driver["full_name"]
                ),
                "registration_status": (
                    driver[
                        "registration_status"
                    ]
                ),
                "identity_verification_status": (
                    driver[
                        "identity_verification_status"
                    ]
                ),
                "vehicle_verification_status": (
                    driver[
                        "vehicle_verification_status"
                    ]
                ),
                "operational_status": (
                    driver[
                        "operational_status"
                    ]
                ),
                "is_online": (
                    driver["is_online"]
                ),
                "is_available": (
                    driver["is_available"]
                ),
                "has_active_ride": (
                    driver["has_active_ride"]
                ),
                "active_vehicle": (
                    driver["active_vehicle"]
                ),
                "available_actions": (
                    _build_available_actions(
                        driver
                    )
                ),
            }
        )

    return summaries