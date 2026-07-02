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


def get_rides_by_passenger(passenger_id):
    connection = create_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            distance,
            fare,
            status
        FROM rides
        WHERE passenger_id = ?
        ORDER BY id DESC
        """,
        (passenger_id,),
    )

    rides = cursor.fetchall()

    connection.close()

    return rides