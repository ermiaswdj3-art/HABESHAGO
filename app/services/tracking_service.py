from app.state.live_tracking_state import live_tracking


def update_driver_location(
    driver_id,
    passenger_id,
    latitude,
    longitude,
):
    """
    Store the driver's latest live location.
    """

    live_tracking[driver_id] = {
        "passenger_id": passenger_id,
        "latitude": latitude,
        "longitude": longitude,
    }


def get_driver_location(driver_id):
    """
    Return the driver's latest location.
    """

    return live_tracking.get(driver_id)


def remove_driver_location(driver_id):
    """
    Remove driver from live tracking.
    """

    if driver_id in live_tracking:
        del live_tracking[driver_id]