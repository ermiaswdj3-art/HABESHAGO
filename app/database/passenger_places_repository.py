from app.database.database import (
    create_connection,
)


def create_passenger_places_table():
    """
    Create the passenger_places table.
    """

    connection = create_connection()
    cursor = connection.cursor()

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def save_place(
    passenger_id,
    place_type,
    place_name,
    full_address,
    latitude,
    longitude,
):
    """
    Save a passenger place.

    Home and work replace older entries.
    Favorites and recent places may have
    multiple entries.
    """

    connection = create_connection()
    cursor = connection.cursor()

    if place_type in ("home", "work"):
        cursor.execute(
            """
            DELETE FROM passenger_places
            WHERE passenger_id = ?
              AND place_type = ?
            """,
            (
                passenger_id,
                place_type,
            ),
        )

    cursor.execute(
        """
        INSERT INTO passenger_places (
            passenger_id,
            place_type,
            place_name,
            full_address,
            latitude,
            longitude
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            passenger_id,
            place_type,
            place_name,
            full_address,
            latitude,
            longitude,
        ),
    )

    connection.commit()
    connection.close()


def save_home(
    passenger_id,
    place_name,
    full_address,
    latitude,
    longitude,
):
    """
    Save or replace the passenger's home.
    """

    save_place(
        passenger_id=passenger_id,
        place_type="home",
        place_name=place_name,
        full_address=full_address,
        latitude=latitude,
        longitude=longitude,
    )


def save_work(
    passenger_id,
    place_name,
    full_address,
    latitude,
    longitude,
):
    """
    Save or replace the passenger's workplace.
    """

    save_place(
        passenger_id=passenger_id,
        place_type="work",
        place_name=place_name,
        full_address=full_address,
        latitude=latitude,
        longitude=longitude,
    )


def save_favorite(
    passenger_id,
    place_name,
    full_address,
    latitude,
    longitude,
):
    """
    Save a passenger favorite place.
    """

    save_place(
        passenger_id=passenger_id,
        place_type="favorite",
        place_name=place_name,
        full_address=full_address,
        latitude=latitude,
        longitude=longitude,
    )


def save_recent_place(
    passenger_id,
    place_name,
    full_address,
    latitude,
    longitude,
):
    """
    Save a recently selected destination.

    An existing matching recent destination is
    removed first so it returns to the top.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM passenger_places
        WHERE passenger_id = ?
          AND place_type = 'recent'
          AND ROUND(latitude, 5) = ROUND(?, 5)
          AND ROUND(longitude, 5) = ROUND(?, 5)
        """,
        (
            passenger_id,
            latitude,
            longitude,
        ),
    )

    cursor.execute(
        """
        INSERT INTO passenger_places (
            passenger_id,
            place_type,
            place_name,
            full_address,
            latitude,
            longitude
        )
        VALUES (?, 'recent', ?, ?, ?, ?)
        """,
        (
            passenger_id,
            place_name,
            full_address,
            latitude,
            longitude,
        ),
    )

    connection.commit()
    connection.close()


def get_place(
    passenger_id,
    place_type,
):
    """
    Return the passenger's latest place
    for a specific type.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            place_name,
            full_address,
            latitude,
            longitude,
            created_at
        FROM passenger_places
        WHERE passenger_id = ?
          AND place_type = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            passenger_id,
            place_type,
        ),
    )

    place = cursor.fetchone()

    connection.close()

    return place


def get_home(passenger_id):
    """
    Return the passenger's saved home.
    """

    return get_place(
        passenger_id,
        "home",
    )


def get_work(passenger_id):
    """
    Return the passenger's saved workplace.
    """

    return get_place(
        passenger_id,
        "work",
    )


def get_favorites(
    passenger_id,
    limit=5,
):
    """
    Return the passenger's latest favorites.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            place_name,
            full_address,
            latitude,
            longitude,
            created_at
        FROM passenger_places
        WHERE passenger_id = ?
          AND place_type = 'favorite'
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            passenger_id,
            limit,
        ),
    )

    places = cursor.fetchall()

    connection.close()

    return places


def get_recent_places(
    passenger_id,
    limit=5,
):
    """
    Return the passenger's latest destinations.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            place_name,
            full_address,
            latitude,
            longitude,
            created_at
        FROM passenger_places
        WHERE passenger_id = ?
          AND place_type = 'recent'
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            passenger_id,
            limit,
        ),
    )

    places = cursor.fetchall()

    connection.close()

    return places