from app.database.database import create_connection


def save_ride(
    passenger_id,
    driver_id,
    pickup_latitude,
    pickup_longitude,
    destination_latitude,
    destination_longitude,
    distance,
    fare,
    status,
):
    """
    Save a new ride.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO rides (
            passenger_id,
            driver_id,
            pickup_latitude,
            pickup_longitude,
            destination_latitude,
            destination_longitude,
            distance,
            fare,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            passenger_id,
            driver_id,
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
    """
    Return all rides for one passenger.
    """

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


def get_latest_confirmed_ride(passenger_id):
    """
    Return the latest confirmed ride.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            driver_id
        FROM rides
        WHERE passenger_id = ?
        AND status = 'Confirmed'
        ORDER BY id DESC
        LIMIT 1
        """,
        (passenger_id,),
    )

    ride = cursor.fetchone()

    connection.close()

    return ride


def get_latest_completed_ride(passenger_id):
    """
    Return the latest completed ride waiting for rating.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            driver_id
        FROM rides
        WHERE passenger_id = ?
        AND status = 'Completed'
        AND driver_rating IS NULL
        ORDER BY id DESC
        LIMIT 1
        """,
        (passenger_id,),
    )

    ride = cursor.fetchone()

    connection.close()

    return ride


def complete_ride(ride_id):
    """
    Mark a ride as completed.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE rides
        SET status = 'Completed'
        WHERE id = ?
        """,
        (ride_id,),
    )

    connection.commit()
    connection.close()


def rate_driver(ride_id, rating):
    """
    Save passenger rating.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE rides
        SET driver_rating = ?
        WHERE id = ?
        """,
        (
            rating,
            ride_id,
        ),
    )

    connection.commit()
    connection.close()


def rate_passenger(ride_id, rating):
    """
    Save driver rating.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE rides
        SET passenger_rating = ?
        WHERE id = ?
        """,
        (
            rating,
            ride_id,
        ),
    )

    connection.commit()
    connection.close()