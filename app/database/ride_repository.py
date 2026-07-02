from app.database.database import create_connection


def save_ride(
    passenger_id,
    pickup_latitude,
    pickup_longitude,
    destination_latitude,
    destination_longitude,
    distance,
    fare,
    status,
):
    connection = create_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO rides (
            passenger_id,
            pickup_latitude,
            pickup_longitude,
            destination_latitude,
            destination_longitude,
            distance,
            fare,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            passenger_id,
            pickup_latitude,
            pickup_longitude,
            destination_latitude,
            destination_longitude,
            distance,
            fare,
            status,
        ),
    )

    connection.commit()
    connection.close()