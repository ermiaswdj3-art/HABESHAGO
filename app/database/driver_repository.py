from app.database.database import create_connection


def register_driver(
    telegram_id,
    full_name,
    phone_number,
    vehicle,
    vehicle_year,
    vehicle_color,
    plate_number,
    latitude,
    longitude,
):

    """
    Register a new driver.
    """

    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO drivers (
                telegram_id,
                full_name,
                phone_number,
                vehicle,
                vehicle_year,
                vehicle_color,
                plate_number,
                latitude,
                longitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                full_name,
                phone_number,
                vehicle,
                vehicle_year,
                vehicle_color,
                plate_number,
                latitude,
                longitude,
            ),
        )

        connection.commit()
        connection.close()

        print("✅ Driver registered successfully!")

    except Exception as e:
        print("❌ DRIVER REGISTRATION ERROR:")
        print(e)
        raise


def get_driver_by_telegram_id(telegram_id):
    """
    Return a driver's profile using their Telegram ID.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            full_name,
            phone_number,
            vehicle,
            vehicle_year,
            vehicle_color,
            plate_number,
            rating,
            is_available
        FROM drivers
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    driver = cursor.fetchone()

    connection.close()

    return driver    

def get_available_drivers():
    """
    Return all drivers that are online and available.
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
          AND is_online = 1
        """
    )

    drivers = cursor.fetchall()

    print("\n===== AVAILABLE DRIVERS =====")
    print(drivers)
    print("=============================\n")

    connection.close()

    return drivers


def set_driver_unavailable(telegram_id):
    """
    Mark a driver as unavailable.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE drivers
        SET is_available = 0
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    connection.commit()
    connection.close()


def set_driver_available(telegram_id):
    """
    Mark a driver as available.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE drivers
        SET is_available = 1
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    connection.commit()
    connection.close()

def set_driver_online(driver_id):
    """
    Mark driver as online.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE drivers
        SET is_online = 1
        WHERE telegram_id = ?
        """,
        (driver_id,),
    )

    connection.commit()
    connection.close()


def set_driver_offline(driver_id):
    """
    Mark driver as offline.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE drivers
        SET is_online = 0
        WHERE telegram_id = ?
        """,
        (driver_id,),
    )

    connection.commit()
    connection.close()


def update_driver_rating(driver_id):
    """
    Update a driver's average rating based on completed rides.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT AVG(driver_rating)
        FROM rides
        WHERE driver_id = ?
          AND driver_rating IS NOT NULL
        """,
        (driver_id,),
    )

    result = cursor.fetchone()

    average_rating = result[0] if result[0] is not None else 5.0

    cursor.execute(
        """
        UPDATE drivers
        SET rating = ?
        WHERE telegram_id = ?
        """,
        (
            round(average_rating, 2),
            driver_id,
        ),
    )

    connection.commit()
    connection.close()
    
def get_driver_by_id(telegram_id):
    """
    Return one driver's information by Telegram ID.
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
            rating
        FROM drivers
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    driver = cursor.fetchone()

    connection.close()

    return driver   