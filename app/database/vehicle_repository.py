"""
HABESHAGO Vehicle Repository

Provides persistent access to canonical vehicle records.
"""

from app.database.database import create_connection
from app.models import Vehicle


def create_vehicle(
    vehicle: Vehicle,
) -> Vehicle:
    """
    Store one canonical vehicle record.
    """

    vehicle.validate()

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO vehicles (
                driver_id,
                vehicle_type,
                brand,
                model,
                manufacturing_year,
                color,
                plate_type,
                plate_region,
                plate_number,
                category,
                verification_status,
                is_active,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """,
            (
                vehicle.driver_id,
                vehicle.vehicle_type,
                vehicle.brand,
                vehicle.model,
                vehicle.manufacturing_year,
                vehicle.color,
                vehicle.plate_type,
                vehicle.plate_region,
                vehicle.plate_number,
                vehicle.category,
                vehicle.verification_status,
                int(vehicle.is_active),
            ),
        )

        vehicle.vehicle_id = cursor.lastrowid

        connection.commit()

        return vehicle

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_vehicle_by_id(
    vehicle_id: int,
) -> Vehicle | None:
    """
    Return one vehicle by its internal ID.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            driver_id,
            vehicle_type,
            brand,
            model,
            manufacturing_year,
            color,
            plate_type,
            plate_region,
            plate_number,
            category,
            verification_status,
            is_active,
            created_at,
            updated_at
        FROM vehicles
        WHERE id = ?
        """,
        (vehicle_id,),
    )

    row = cursor.fetchone()

    connection.close()

    return _row_to_vehicle(row)


def get_driver_vehicles(
    driver_id: int,
) -> list[Vehicle]:
    """
    Return every vehicle owned by one driver.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            driver_id,
            vehicle_type,
            brand,
            model,
            manufacturing_year,
            color,
            plate_type,
            plate_region,
            plate_number,
            category,
            verification_status,
            is_active,
            created_at,
            updated_at
        FROM vehicles
        WHERE driver_id = ?
        ORDER BY is_active DESC, id ASC
        """,
        (driver_id,),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        _row_to_vehicle(row)
        for row in rows
    ]


def get_active_driver_vehicle(
    driver_id: int,
) -> Vehicle | None:
    """
    Return the active vehicle for one driver.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            driver_id,
            vehicle_type,
            brand,
            model,
            manufacturing_year,
            color,
            plate_type,
            plate_region,
            plate_number,
            category,
            verification_status,
            is_active,
            created_at,
            updated_at
        FROM vehicles
        WHERE driver_id = ?
          AND is_active = 1
        ORDER BY id ASC
        LIMIT 1
        """,
        (driver_id,),
    )

    row = cursor.fetchone()

    connection.close()

    return _row_to_vehicle(row)


def _row_to_vehicle(
    row,
) -> Vehicle | None:
    """
    Convert a repository row into a Vehicle model.
    """

    if row is None:
        return None

    return Vehicle(
        vehicle_id=row[0],
        driver_id=row[1],
        vehicle_type=row[2],
        brand=row[3],
        model=row[4],
        manufacturing_year=row[5],
        color=row[6],
        plate_type=row[7],
        plate_region=row[8],
        plate_number=row[9],
        category=row[10],
        verification_status=row[11],
        is_active=bool(row[12]),
        created_at=row[13],
        updated_at=row[14],
    )