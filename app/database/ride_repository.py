from app.constants.ride_status import (
    ACCEPTED,
    CANCELLED,
    DRIVER_ARRIVED,
    DRIVER_ARRIVING,
    EXPIRED,
    RATED,
    REQUESTED,
    TRIP_COMPLETED,
    TRIP_STARTED,
)

from app.database.database import (
    create_connection,
)

from app.services.earnings_service import (
    calculate_earnings,
)


ACTIVE_RIDE_STATUSES = (
    ACCEPTED,
    DRIVER_ARRIVING,
    DRIVER_ARRIVED,
    TRIP_STARTED,
)


# ==============================================
# INTERNAL LIFECYCLE HELPERS
# ==============================================

def _update_status_and_timestamp(
    ride_id,
    status,
    timestamp_column,
):
    """
    Update a ride's status and record the time
    of the lifecycle transition.

    timestamp_column is supplied only by trusted
    internal HABESHAGO code.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        f"""
        UPDATE rides
        SET
            status = ?,
            {timestamp_column} = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            status,
            ride_id,
        ),
    )

    connection.commit()
    connection.close()


# ==============================================
# SAVE RIDE
# ==============================================

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
    Save a new ride with:

    - lifecycle timestamps;
    - HABESHAGO commission;
    - driver earnings.

    Returns the newly created ride ID.
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
            service_type,
            commission_rate,
            commission_amount,
            driver_earnings,
            status,
            created_at,
            requested_at
        )
        VALUES (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        """,
        (
            passenger_id,
            driver_id,
            pickup_latitude,
            pickup_longitude,
            destination_latitude,
            destination_longitude,
            distance,
            earnings["fare"],
            service_type,
            earnings["commission_rate"],
            earnings["commission_amount"],
            earnings["driver_earnings"],
            status,
        ),
    )

    ride_id = cursor.lastrowid

    # HABESHAGO currently creates the database ride
    # when the driver accepts the request.
    if status in {
        ACCEPTED,
        DRIVER_ARRIVING,
        DRIVER_ARRIVED,
        TRIP_STARTED,
        TRIP_COMPLETED,
    }:
        cursor.execute(
            """
            UPDATE rides
            SET accepted_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (ride_id,),
        )

    connection.commit()
    connection.close()

    return ride_id


# ==============================================
# LIFECYCLE TRANSITIONS
# ==============================================

def mark_ride_requested(ride_id):
    """
    Mark a ride as requested.
    """

    _update_status_and_timestamp(
        ride_id,
        REQUESTED,
        "requested_at",
    )


def mark_ride_accepted(ride_id):
    """
    Mark a ride as accepted by a driver.
    """

    _update_status_and_timestamp(
        ride_id,
        ACCEPTED,
        "accepted_at",
    )


def mark_driver_arriving(ride_id):
    """
    Mark the driver as travelling toward pickup.
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
            DRIVER_ARRIVING,
            ride_id,
        ),
    )

    connection.commit()
    connection.close()


def mark_driver_arrived(ride_id):
    """
    Record that the driver reached pickup.
    """

    _update_status_and_timestamp(
        ride_id,
        DRIVER_ARRIVED,
        "arrived_at",
    )


def mark_trip_started(ride_id):
    """
    Record that the trip started.
    """

    _update_status_and_timestamp(
        ride_id,
        TRIP_STARTED,
        "started_at",
    )


def mark_trip_completed(ride_id):
    """
    Record that the trip completed.
    """

    _update_status_and_timestamp(
        ride_id,
        TRIP_COMPLETED,
        "completed_at",
    )


def mark_ride_cancelled(ride_id):
    """
    Record that the ride was cancelled.
    """

    _update_status_and_timestamp(
        ride_id,
        CANCELLED,
        "cancelled_at",
    )


def mark_ride_expired(ride_id):
    """
    Record that the ride request expired.
    """

    _update_status_and_timestamp(
        ride_id,
        EXPIRED,
        "expired_at",
    )


# ==============================================
# STATUS COMPATIBILITY FUNCTIONS
# ==============================================

def update_ride_status(
    ride_id,
    status,
):
    """
    Update the ride status.

    Existing handlers may continue calling this
    function. Lifecycle timestamps are recorded
    automatically for recognized transitions.
    """

    transition_functions = {
        REQUESTED: mark_ride_requested,
        ACCEPTED: mark_ride_accepted,
        DRIVER_ARRIVING: mark_driver_arriving,
        DRIVER_ARRIVED: mark_driver_arrived,
        TRIP_STARTED: mark_trip_started,
        TRIP_COMPLETED: mark_trip_completed,
        CANCELLED: mark_ride_cancelled,
        EXPIRED: mark_ride_expired,
    }

    transition_function = (
        transition_functions.get(status)
    )

    if transition_function is not None:
        transition_function(ride_id)
        return

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


def complete_ride(ride_id):
    """
    Mark a ride as completed and record completed_at.

    This function is retained for compatibility
    with the current completion handler.
    """

    mark_trip_completed(ride_id)


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


# ==============================================
# PASSENGER RIDE QUERIES
# ==============================================

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
    Return the passenger's latest confirmed
    or recently completed ride.
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
          AND status IN (?, ?, ?, ?, ?)
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            passenger_id,
            ACCEPTED,
            DRIVER_ARRIVING,
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
    Return the latest completed ride waiting
    for a passenger rating.
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


def get_latest_passenger_ride(passenger_id):
    """
    Return the passenger's latest ride.
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


# ==============================================
# DRIVER RIDE QUERIES
# ==============================================

def get_latest_driver_ride(driver_id):
    """
    Return the latest active ride for a driver.
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
        WHERE driver_id = ?
          AND status IN (?, ?, ?, ?)
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            driver_id,
            ACCEPTED,
            DRIVER_ARRIVING,
            DRIVER_ARRIVED,
            TRIP_STARTED,
        ),
    )

    ride = cursor.fetchone()

    connection.close()

    return ride


def get_driver_rides(driver_id):
    """
    Return all rides assigned to a driver.
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


# ==============================================
# RATINGS
# ==============================================

def rate_driver(
    ride_id,
    rating,
):
    """
    Save the passenger's rating of the driver.
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


def rate_passenger(
    ride_id,
    rating,
):
    """
    Save the driver's rating of the passenger.
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


# ==============================================
# FINANCIAL QUERIES
# ==============================================

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


# ==============================================
# LIFECYCLE ANALYTICS
# ==============================================

def get_ride_lifecycle(ride_id):
    """
    Return the complete lifecycle and timestamps
    for one ride.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            status,
            created_at,
            requested_at,
            accepted_at,
            arrived_at,
            started_at,
            completed_at,
            cancelled_at,
            expired_at
        FROM rides
        WHERE id = ?
        """,
        (ride_id,),
    )

    lifecycle = cursor.fetchone()

    connection.close()

    return lifecycle