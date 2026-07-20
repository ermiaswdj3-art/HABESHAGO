import os
import sqlite3


DATABASE_NAME = "habeshago.db"


def create_connection():
    """
    Create and return a connection to the HABESHAGO database.
    """

    database_path = os.path.abspath(
        DATABASE_NAME
    )

    print("\n==============================")
    print("DATABASE:", database_path)
    print("==============================\n")

    connection = sqlite3.connect(
        database_path
    )

    return connection


def create_tables():
    """
    Create all HABESHAGO database tables.
    """

    connection = create_connection()
    cursor = connection.cursor()

    # ==========================================
    # PASSENGERS TABLE
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone_number TEXT,
            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ==========================================
    # DRIVERS TABLE
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone_number TEXT,

            vehicle TEXT NOT NULL,
            vehicle_year INTEGER NOT NULL,
            vehicle_color TEXT NOT NULL,
            plate_number TEXT UNIQUE NOT NULL,

            rating REAL DEFAULT 5.0,

            is_available INTEGER DEFAULT 1,
            is_online INTEGER DEFAULT 0,

            latitude REAL NOT NULL,
            longitude REAL NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # ==========================================
    # RIDES TABLE
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            passenger_id INTEGER NOT NULL,
            driver_id INTEGER NOT NULL,

            pickup_latitude REAL NOT NULL,
            pickup_longitude REAL NOT NULL,

            destination_latitude REAL NOT NULL,
            destination_longitude REAL NOT NULL,

            distance REAL NOT NULL,
            fare REAL NOT NULL,

            service_type TEXT DEFAULT 'fuel',

            commission_rate REAL DEFAULT 0.10,
            commission_amount REAL DEFAULT 0,
            driver_earnings REAL DEFAULT 0,

            status TEXT DEFAULT 'requested',

            driver_rating INTEGER,
            passenger_rating INTEGER,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (passenger_id)
                REFERENCES passengers (telegram_id),

            FOREIGN KEY (driver_id)
                REFERENCES drivers (telegram_id)
        )
        """
    )

    # ==========================================
    # PASSENGER PLACES TABLE
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS passenger_places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            passenger_id INTEGER NOT NULL,

            place_type TEXT NOT NULL,
            place_name TEXT NOT NULL,
            full_address TEXT,

            latitude REAL NOT NULL,
            longitude REAL NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (passenger_id)
                REFERENCES passengers (telegram_id)
        )
        """
    )

    # ==========================================
    # DATABASE INDEXES
    # ==========================================

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_rides_passenger_id
        ON rides (passenger_id)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_rides_driver_id
        ON rides (driver_id)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_rides_status
        ON rides (status)
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_passenger_places_passenger
        ON passenger_places (
            passenger_id,
            place_type
        )
        """
    )

    connection.commit()
    connection.close()