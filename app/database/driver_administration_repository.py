"""
HABESHAGO Driver Administration Repository

Performs canonical driver-governance transitions and
writes durable audit records inside the same transaction.

This repository owns persistence only.
Business transition rules belong to the shared
Driver Administration Service.
"""

from uuid import uuid4

from app.constants.driver_admin_actions import (
    DRIVER_ADMIN_ACTIONS,
)

from app.constants.ride_status import (
    ACCEPTED,
    DRIVER_ARRIVED,
    DRIVER_ARRIVING,
    TRIP_STARTED,
)

from app.database.database import (
    create_connection,
)


ACTIVE_RIDE_STATUSES = (
    ACCEPTED,
    DRIVER_ARRIVING,
    DRIVER_ARRIVED,
    TRIP_STARTED,
)


def _build_action_reference(
    action_type: str,
) -> str:
    """
    Return a unique Driver Administration reference.
    """

    return (
        "DRIVER-ADMIN-"
        f"{action_type}-"
        f"{uuid4().hex[:10].upper()}"
    )


def _load_driver_state(
    cursor,
    driver_id: int,
):
    """
    Load the current driver-governance state.
    """

    cursor.execute(
        """
        SELECT
            telegram_id,
            full_name,
            registration_status,
            identity_verification_status,
            vehicle_verification_status,
            operational_status,
            is_online,
            is_available,
            verified_at,
            rejection_reason
        FROM drivers
        WHERE telegram_id = ?
        """,
        (driver_id,),
    )

    return cursor.fetchone()


def _load_active_vehicle_state(
    cursor,
    driver_id: int,
):
    """
    Load the driver's canonical active vehicle.
    """

    cursor.execute(
        """
        SELECT
            id,
            verification_status,
            is_active
        FROM vehicles
        WHERE driver_id = ?
          AND is_active = 1
        ORDER BY id ASC
        LIMIT 1
        """,
        (driver_id,),
    )

    return cursor.fetchone()


def _load_active_ride_id(
    cursor,
    driver_id: int,
) -> int | None:
    """
    Return the driver's persistent active ride ID.
    """

    placeholders = ", ".join(
        "?"
        for _ in ACTIVE_RIDE_STATUSES
    )

    cursor.execute(
        f"""
        SELECT id
        FROM rides
        WHERE driver_id = ?
          AND status IN (
              {placeholders}
          )
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            driver_id,
            *ACTIVE_RIDE_STATUSES,
        ),
    )

    row = cursor.fetchone()

    if row is None:
        return None

    return int(row[0])


def get_driver_management_record(
    driver_id: int,
) -> dict | None:
    """
    Return one complete persistent driver-management record.
    """

    connection = create_connection()
    cursor = connection.cursor()

    driver = _load_driver_state(
        cursor,
        driver_id,
    )

    if driver is None:
        connection.close()
        return None

    vehicle = _load_active_vehicle_state(
        cursor,
        driver_id,
    )

    active_ride_id = _load_active_ride_id(
        cursor,
        driver_id,
    )

    connection.close()

    return {
        "driver_id": int(driver[0]),
        "full_name": driver[1],
        "registration_status": (
            driver[2]
        ),
        "identity_verification_status": (
            driver[3]
        ),
        "vehicle_verification_status": (
            driver[4]
        ),
        "operational_status": driver[5],
        "is_online": bool(driver[6]),
        "is_available": bool(driver[7]),
        "verified_at": driver[8],
        "rejection_reason": driver[9],
        "active_vehicle": (
            {
                "vehicle_id": int(
                    vehicle[0]
                ),
                "verification_status": (
                    vehicle[1]
                ),
                "is_active": bool(
                    vehicle[2]
                ),
            }
            if vehicle is not None
            else None
        ),
        "active_ride_id": active_ride_id,
        "has_active_ride": (
            active_ride_id is not None
        ),
    }


def list_driver_management_records() -> list[dict]:
    """
    Return every driver with canonical management data.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT telegram_id
        FROM drivers
        ORDER BY registration_submitted_at DESC,
                 created_at DESC,
                 telegram_id ASC
        """
    )

    driver_ids = [
        int(row[0])
        for row in cursor.fetchall()
    ]

    connection.close()

    records = []

    for driver_id in driver_ids:
        record = get_driver_management_record(
            driver_id
        )

        if record is not None:
            records.append(
                record
            )

    return records


def apply_driver_admin_transition(
    *,
    driver_id: int,
    actor_id: int,
    action_type: str,
    new_registration_status: str,
    new_identity_status: str,
    new_vehicle_status: str,
    new_operational_status: str,
    reason: str | None,
    update_verified_at: bool,
) -> dict:
    """
    Atomically update driver governance, active-vehicle
    verification, operational state, and audit history.
    """

    if action_type not in DRIVER_ADMIN_ACTIONS:
        raise ValueError(
            "Invalid driver administration action."
        )

    action_reference = (
        _build_action_reference(
            action_type
        )
    )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        previous_driver = (
            _load_driver_state(
                cursor,
                driver_id,
            )
        )

        if previous_driver is None:
            raise ValueError(
                "Driver profile not found."
            )

        active_vehicle = (
            _load_active_vehicle_state(
                cursor,
                driver_id,
            )
        )

        if active_vehicle is None:
            raise ValueError(
                "Driver has no active vehicle."
            )

        active_ride_id = (
            _load_active_ride_id(
                cursor,
                driver_id,
            )
        )

        previous_registration_status = (
            previous_driver[2]
        )

        previous_identity_status = (
            previous_driver[3]
        )

        previous_vehicle_status = (
            previous_driver[4]
        )

        previous_operational_status = (
            previous_driver[5]
        )

        verified_at_expression = (
            "CURRENT_TIMESTAMP"
            if update_verified_at
            else "verified_at"
        )

        cursor.execute(
            f"""
            UPDATE drivers
            SET
                registration_status = ?,
                identity_verification_status = ?,
                vehicle_verification_status = ?,
                operational_status = ?,
                is_online = 0,
                is_available = 0,
                operational_status_updated_at =
                    CURRENT_TIMESTAMP,
                verified_at = (
                    {verified_at_expression}
                ),
                rejection_reason = ?
            WHERE telegram_id = ?
            """,
            (
                new_registration_status,
                new_identity_status,
                new_vehicle_status,
                new_operational_status,
                reason,
                driver_id,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "Driver transition could not be applied."
            )

        cursor.execute(
            """
            UPDATE vehicles
            SET
                verification_status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                new_vehicle_status,
                active_vehicle[0],
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "Active vehicle transition could not "
                "be applied."
            )

        cursor.execute(
            """
            INSERT INTO driver_admin_actions (
                action_reference,
                driver_id,
                actor_id,
                action_type,
                previous_registration_status,
                new_registration_status,
                previous_identity_status,
                new_identity_status,
                previous_vehicle_status,
                new_vehicle_status,
                previous_operational_status,
                new_operational_status,
                reason,
                created_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                CURRENT_TIMESTAMP
            )
            """,
            (
                action_reference,
                driver_id,
                actor_id,
                action_type,
                previous_registration_status,
                new_registration_status,
                previous_identity_status,
                new_identity_status,
                previous_vehicle_status,
                new_vehicle_status,
                previous_operational_status,
                new_operational_status,
                reason,
            ),
        )

        cursor.execute(
            """
            SELECT
                id,
                action_reference,
                driver_id,
                actor_id,
                action_type,
                previous_registration_status,
                new_registration_status,
                previous_identity_status,
                new_identity_status,
                previous_vehicle_status,
                new_vehicle_status,
                previous_operational_status,
                new_operational_status,
                reason,
                created_at
            FROM driver_admin_actions
            WHERE action_reference = ?
            """,
            (action_reference,),
        )

        audit_row = cursor.fetchone()

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    if audit_row is None:
        raise RuntimeError(
            "Driver administration audit record "
            "could not be loaded."
        )

    return {
        "action_id": int(audit_row[0]),
        "action_reference": audit_row[1],
        "driver_id": int(audit_row[2]),
        "actor_id": int(audit_row[3]),
        "action_type": audit_row[4],
        "previous_registration_status": (
            audit_row[5]
        ),
        "new_registration_status": (
            audit_row[6]
        ),
        "previous_identity_status": (
            audit_row[7]
        ),
        "new_identity_status": audit_row[8],
        "previous_vehicle_status": (
            audit_row[9]
        ),
        "new_vehicle_status": audit_row[10],
        "previous_operational_status": (
            audit_row[11]
        ),
        "new_operational_status": (
            audit_row[12]
        ),
        "reason": audit_row[13],
        "created_at": audit_row[14],
        "active_ride_id_at_transition": (
            active_ride_id
        ),
    }


def get_driver_admin_actions(
    driver_id: int,
) -> list[dict]:
    """
    Return one driver's durable administration history.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            action_reference,
            actor_id,
            action_type,
            previous_registration_status,
            new_registration_status,
            reason,
            created_at
        FROM driver_admin_actions
        WHERE driver_id = ?
        ORDER BY id DESC
        """,
        (driver_id,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "action_id": int(row[0]),
            "action_reference": row[1],
            "actor_id": int(row[2]),
            "action_type": row[3],
            "previous_registration_status": (
                row[4]
            ),
            "new_registration_status": row[5],
            "reason": row[6],
            "created_at": row[7],
        }
        for row in rows
    ]