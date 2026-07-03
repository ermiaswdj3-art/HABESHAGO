import sqlite3

DATABASE_NAME = "habeshago.db"


def create_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(DATABASE_NAME)
    return connection


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

    # Rides table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_id INTEGER NOT NULL,
            pickup_latitude REAL NOT NULL,
            pickup_longitude REAL NOT NULL,
            destination_latitude REAL NOT NULL,
            destination_longitude REAL NOT NULL,
            distance REAL NOT NULL,
            fare REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (passenger_id)
                REFERENCES passengers (telegram_id)
        )
    """)

    connection.commit()
    connection.close()