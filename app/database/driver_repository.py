from app.database.database import create_connection

from app.models import Vehicle

def register_driver(
    telegram_id,
    full_name,
    phone_number,
    vehicle_type,
    vehicle_brand,
    vehicle_model,
    vehicle_year,
    vehicle_color,
    plate_type,
    plate_region,
    plate_number,
    latitude,
    longitude,
):
    """
    Register a driver application and its first vehicle
    in one atomic database transaction.

    Newly submitted drivers and vehicles remain pending
    verification and cannot enter dispatch until approved.
    """

    clean_vehicle_type = str(
        vehicle_type or ""
    ).strip()

    vehicle_type_map = {
        "⛽ Fuel Car": "fuel_car",
        "Fuel Car": "fuel_car",
        "⚡ Electric Car": "electric_car",
        "Electric Car": "electric_car",
        "🏍 Motorcycle": "motorcycle",
        "Motorcycle": "motorcycle",
    }

    canonical_vehicle_type = (
        vehicle_type_map.get(
            clean_vehicle_type,
            "legacy",
        )
    )

    clean_plate_type = str(
        plate_type or ""
    ).strip()

    plate_type_map = {
        "🟦 Regional Plate": "regional",
        "Regional Plate": "regional",
        "🟩 National ETH Plate": "national_eth",
        "National ETH Plate": "national_eth",
    }

    canonical_plate_type = (
        plate_type_map.get(
            clean_plate_type
        )
    )

    canonical_plate_region = (
        str(plate_region).strip()
        if plate_region
        else None
    )

    vehicle_category = (
        "motorcycle"
        if canonical_vehicle_type == "motorcycle"
        else "standard"
    )

    vehicle_record = Vehicle(
        vehicle_id=None,
        driver_id=int(telegram_id),
        vehicle_type=canonical_vehicle_type,
        brand=str(vehicle_brand).strip(),
        model=str(vehicle_model).strip(),
        manufacturing_year=int(
            vehicle_year
        ),
        color=str(vehicle_color).strip(),
        plate_type=canonical_plate_type,
        plate_region=canonical_plate_region,
        plate_number=str(
            plate_number
        ).strip(),
        category=vehicle_category,
        verification_status="pending",
        is_active=True,
    )

    vehicle_record.validate()

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        # ======================================
        # DRIVER APPLICATION
        # ======================================

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
                ?, ?, ?,

                ?, ?, ?, ?,

                ?, ?,

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

                vehicle_record.display_name,
                vehicle_record.manufacturing_year,
                vehicle_record.color,
                vehicle_record.plate_number,

                latitude,
                longitude,
            ),
        )

        # ======================================
        # CANONICAL VEHICLE RECORD
        # ======================================

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
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                'pending',
                1,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """,
            (
                vehicle_record.driver_id,
                vehicle_record.vehicle_type,
                vehicle_record.brand,
                vehicle_record.model,
                vehicle_record.manufacturing_year,
                vehicle_record.color,
                vehicle_record.plate_type,
                vehicle_record.plate_region,
                vehicle_record.plate_number,
                vehicle_record.category,
            ),
        )

        vehicle_record.vehicle_id = (
            cursor.lastrowid
        )

        connection.commit()

        print(
            "✅ Driver application submitted successfully!"
        )
        print(
            "Registration Status : verification_pending"
        )
        print(
            "Identity Status     : pending"
        )
        print(
            "Vehicle Status      : pending"
        )
        print(
            "Vehicle ID          :",
            vehicle_record.vehicle_id,
        )

        return vehicle_record

    except Exception:
        connection.rollback()

        print(
            "❌ DRIVER AND VEHICLE REGISTRATION ERROR"
        )

        raise

    finally:
        connection.close()


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