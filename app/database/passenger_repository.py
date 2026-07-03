from app.database.database import create_connection


def register_passenger(telegram_id, full_name, phone_number=None):
    """
    Register a passenger if they don't already exist.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO passengers (
            telegram_id,
            full_name,
            phone_number
        )
        VALUES (?, ?, ?)
        """,
        (
            telegram_id,
            full_name,
            phone_number,
        ),
    )

    connection.commit()
    connection.close()


def get_passenger(telegram_id):
    """
    Retrieve a passenger by Telegram ID.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            telegram_id,
            full_name,
            phone_number,
            created_at
        FROM passengers
        WHERE telegram_id = ?
        """,
        (telegram_id,),
    )

    passenger = cursor.fetchone()

    connection.close()

    return passenger


def update_phone_number(telegram_id, phone_number):
    """
    Update a passenger's phone number.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE passengers
        SET phone_number = ?
        WHERE telegram_id = ?
        """,
        (
            phone_number,
            telegram_id,
        ),
    )

    connection.commit()
    connection.close()