import sqlite3

DATABASE_NAME = "habeshago.db"


import sqlite3
import os

DATABASE_NAME = "habeshago.db"


def create_connection():
    database_path = os.path.abspath(DATABASE_NAME)

    print("\n==============================")
    print("DATABASE:", database_path)
    print("==============================\n")

    return sqlite3.connect(database_path)


def create_tables():
    """
    Create all database tables.
    """
    connection = create_connection()

    cursor = connection.cursor()

    # Passengers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Drivers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
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

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Rides table
    cursor.execute("""
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

            status TEXT DEFAULT 'requested',

            driver_rating INTEGER,
            passenger_rating INTEGER,

            FOREIGN KEY (passenger_id)
                REFERENCES passengers (telegram_id),

            FOREIGN KEY (driver_id)
                REFERENCES drivers (telegram_id)
        )
    """)

    connection.commit()
    connection.close()