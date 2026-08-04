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

    Newly registered drivers are placed into the
    verification workflow and cannot receive ride
    requests until approved.
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
                longitude,

                registration_status,
                identity_verification_status,
                vehicle_verification_status,
                registration_submitted_at,

                is_available,
                is_online
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,

                'verification_pending',
                'pending',
                'pending',
                CURRENT_TIMESTAMP,

                0,
                0
            )
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
        print("Registration Status : verification_pending")
        print("Identity Status     : pending")
        print("Vehicle Status      : pending")

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

def get_driver_registration_profile(
    telegram_id,
):
    """
    Return the persistent driver registration and
    verification profile for one Telegram user.

    This contract is used by shared HABESHAGO services
    and future client interfaces.
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
            vehicle_year,
            vehicle_color,
            plate_number,
            registration_status,
            identity_verification_status,
            vehicle_verification_status,
            registration_submitted_at,
            verified_at,
            rejection_reason
        FROM drivers
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    registration = cursor.fetchone()

    connection.close()

    return registration

def get_driver_dashboard_profile(
    telegram_id,
):
    """
    Return the complete driver profile used by
    shared dashboard clients.

    This richer query preserves the existing
    get_driver_by_telegram_id() contract.
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
            vehicle_year,
            vehicle_color,
            plate_number,
            rating,
            is_online,
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
          AND registration_status = 'approved'
          AND identity_verification_status = 'verified'
          AND vehicle_verification_status = 'verified'
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

def update_driver_location(
    driver_id,
    latitude,
    longitude,
):
    """
    Update a driver's current location.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE drivers
        SET latitude = ?,
            longitude = ?
        WHERE telegram_id = ?
        """,
        (
            latitude,
            longitude,
            driver_id,
        ),
    )

    connection.commit()

    connection.close()

def get_driver_profile(driver_id):
    """
    Return the driver's profile information.
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
            is_online,
            is_available
        FROM drivers
        WHERE telegram_id = ?
        """,
        (driver_id,),
    )

    driver = cursor.fetchone()

    connection.close()

    return driver   