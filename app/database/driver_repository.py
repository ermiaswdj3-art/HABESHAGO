from app.database.database import create_connection


def register_driver(
    telegram_id,
    full_name,
    phone_number,
    vehicle,
    vehicle_color,
    plate_number,
    latitude,
    longitude,
):
    """
    Register a new driver.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO drivers (
            telegram_id,
            full_name,
            phone_number,
            vehicle,
            vehicle_color,
            plate_number,
            latitude,
            longitude
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            telegram_id,
            full_name,
            phone_number,
            vehicle,
            vehicle_color,
            plate_number,
            latitude,
            longitude,
        ),
    )

    connection.commit()
    connection.close()


def get_available_drivers():
    """
    Return all available drivers.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            telegram_id,
            full_name,
            phone_number,
            vehicle,
            vehicle_color,
            plate_number,
            rating,
            latitude,
            longitude
        FROM drivers
        WHERE is_available = 1
        """
    )

    drivers = cursor.fetchall()

    connection.close()

    return drivers