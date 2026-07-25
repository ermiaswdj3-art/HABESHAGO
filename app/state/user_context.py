from app.config.settings import (
    ADMIN_ID,
)

from app.database.driver_repository import (
    get_driver_by_telegram_id,
)

from app.database.passenger_repository import (
    get_passenger,
)

from app.state.active_ride_state import (
    active_rides,
)

from app.state.ride_state import (
    ride_requests,
)


def is_administrator(user_id):
    """
    Return True when the Telegram user is the
    configured HABESHAGO administrator.
    """

    return (
        ADMIN_ID is not None
        and str(user_id) == str(ADMIN_ID)
    )


def get_active_driver_ride(user_id):
    """
    Return the driver's active in-memory ride,
    or None when no active ride exists.
    """

    return active_rides.get(user_id)


def get_user_context(user_id):
    """
    Build a current context summary for one user.

    This function reads HABESHAGO's existing
    state and database records. It does not
    create a competing source of truth.
    """

    driver = get_driver_by_telegram_id(
        user_id
    )

    passenger = get_passenger(
        user_id
    )

    active_driver_ride = (
        get_active_driver_ride(
            user_id
        )
    )

    passenger_ride_request = (
        ride_requests.get(
            user_id
        )
    )

    return {
        "user_id": user_id,
        "is_admin": is_administrator(
            user_id
        ),
        "is_driver": driver is not None,
        "is_passenger": passenger is not None,
        "has_active_driver_ride": (
            active_driver_ride is not None
        ),
        "active_driver_ride": (
            active_driver_ride
        ),
        "has_passenger_ride_request": (
            passenger_ride_request is not None
        ),
        "passenger_ride_request": (
            passenger_ride_request
        ),
    }