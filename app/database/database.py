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

    return sqlite3.connect(
        database_path
    )


def get_table_columns(
    cursor,
    table_name,
):
    """
    Return the names of all columns in a database table.
    """

    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    return {
        row[1]
        for row in cursor.fetchall()
    }


def add_column_if_missing(
    cursor,
    table_name,
    column_name,
    column_definition,
):
    """
    Add a database column only when it does not exist.

    The table name, column name and definition are supplied
    internally by HABESHAGO—not from user input.
    """

    existing_columns = get_table_columns(
        cursor,
        table_name,
    )

    if column_name in existing_columns:
        return False

    cursor.execute(
        f"""
        ALTER TABLE {table_name}
        ADD COLUMN {column_name} {column_definition}
        """
    )

    print(
        "✅ Database migration added column: "
        f"{table_name}.{column_name}"
    )

    return True


def migrate_rides_table(
    cursor,
):
    """
    Safely upgrade an existing rides table.

    This migration may run every time HABESHAGO starts.
    Existing columns are never added twice.
    """

    # Earlier HABESHAGO databases may not contain
    # the general record-creation timestamp.
    add_column_if_missing(
        cursor,
        "rides",
        "created_at",
        "TIMESTAMP",
    )

    # Full ride lifecycle timestamps.
    add_column_if_missing(
        cursor,
        "rides",
        "requested_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "accepted_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "arrived_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "started_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "completed_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "cancelled_at",
        "TIMESTAMP",
    )

    add_column_if_missing(
        cursor,
        "rides",
        "expired_at",
        "TIMESTAMP",
    )

    # For existing development rides, requested_at can safely
    # inherit created_at when it is available.
    cursor.execute(
        """
        UPDATE rides
        SET requested_at = created_at
        WHERE requested_at IS NULL
          AND created_at IS NOT NULL
        """
    )

    # Existing completed development rides can inherit
    # created_at as a temporary completed_at value.
    #
    # These historical test records will later be cleared
    # during the planned Development Reset before Public Beta.
    cursor.execute(
        """
        UPDATE rides
        SET completed_at = created_at
        WHERE completed_at IS NULL
          AND created_at IS NOT NULL
          AND status = 'TRIP_COMPLETED'
        """
    )


def create_tables():
    """
    Create and safely upgrade all HABESHAGO database tables.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Enable SQLite foreign-key enforcement
        # for this connection.
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        # ======================================
        # PASSENGERS TABLE
        # ======================================

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

        # ======================================
        # DRIVERS TABLE
        # ======================================

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

        # ======================================
        # RIDES TABLE
        # ======================================

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

                status TEXT DEFAULT 'REQUESTED',

                driver_rating INTEGER,
                passenger_rating INTEGER,

                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                requested_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                accepted_at TIMESTAMP,
                arrived_at TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                expired_at TIMESTAMP,

                FOREIGN KEY (passenger_id)
                    REFERENCES passengers (telegram_id),

                FOREIGN KEY (driver_id)
                    REFERENCES drivers (telegram_id)
            )
            """
        )

        # Safely upgrade databases created by
        # earlier HABESHAGO commits.
        migrate_rides_table(
            cursor
        )

        # ======================================
        # PASSENGER PLACES TABLE
        # ======================================

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

        # ======================================
        # DATABASE INDEXES
        # ======================================

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
            idx_rides_created_at
            ON rides (created_at)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_rides_completed_at
            ON rides (completed_at)
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

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()