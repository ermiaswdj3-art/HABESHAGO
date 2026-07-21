from app.database.database import create_connection
from app.constants.ride_status import (
    REQUESTED,
    ACCEPTED,
    DRIVER_ARRIVING,
    DRIVER_ARRIVED,
    TRIP_STARTED,
    TRIP_COMPLETED,
    RATED,
)

from app.services.earnings_service import (
    calculate_earnings,
)

ACTIVE_RIDE_STATUSES = (
    ACCEPTED,
    DRIVER_ARRIVED,
    TRIP_STARTED,
)


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
    service_type="fuel",
):
    """
    Save a new ride together with
    driver earnings and HABESHAGO commission.
    """

    earnings = calculate_earnings(
        fare,
        service_type,
    )

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
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
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
    Return the passenger's complete ride history.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            driver_id,
            distance,
            fare,
            status,
            driver_rating
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
    Return the latest active ride.
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
          AND status IN (?, ?, ?, ?)
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            passenger_id,
            ACCEPTED,
            DRIVER_ARRIVED,
            TRIP_STARTED,
            TRIP_COMPLETED,
        ),
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
          AND status = ?
          AND driver_rating IS NULL
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            passenger_id,
            TRIP_COMPLETED,
        ),
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
        SET status = ?
        WHERE id = ?
        """,
        (
            TRIP_COMPLETED,
            ride_id,
        ),
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

def update_ride_status(ride_id, status):
    """
    Update the current status of a ride.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE rides
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            ride_id,
        ),
    )

    connection.commit()
    connection.close()


def get_ride_status(ride_id):
    """
    Return the current status of a ride.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT status
        FROM rides
        WHERE id = ?
        """,
        (ride_id,),
    )

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    return result[0]

def get_latest_driver_ride(driver_id):
    """
    Return the latest active ride for a driver.
    """

    print("\n========== DRIVER LOOKUP ==========")
    print("Searching for Driver ID:", driver_id)

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            passenger_id,
            driver_id,
            status
        FROM rides
        WHERE driver_id = ?
          AND status IN (?, ?, ?)
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            driver_id,
            ACCEPTED,
            DRIVER_ARRIVED,
            TRIP_STARTED,
        ),
    )

    ride = cursor.fetchone()

    print("Query Result:", ride)
    print("===================================\n")

    connection.close()

    return ride

def get_latest_passenger_ride(passenger_id):
    """
    Return the latest ride for a passenger.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            passenger_id,
            driver_id,
            status
        FROM rides
        WHERE passenger_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (passenger_id,),
    )

    ride = cursor.fetchone()

    connection.close()

    return ride

def get_ride_earnings(ride_id):
    """
    Return the financial breakdown for one ride.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            fare,
            service_type,
            commission_rate,
            commission_amount,
            driver_earnings
        FROM rides
        WHERE id = ?
        """,
        (ride_id,),
    )

    earnings = cursor.fetchone()

    connection.close()

    return earnings

def get_driver_rides(driver_id):
    """
    Return all rides completed by a driver.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            distance,
            fare,
            status,
            driver_rating
        FROM rides
        WHERE driver_id = ?
        ORDER BY id DESC
        """,
        (driver_id,),
    )

    rides = cursor.fetchall()

    connection.close()

    return rides