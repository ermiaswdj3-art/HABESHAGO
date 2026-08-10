"""
HABESHAGO Mini App Ride Integration Models

Small immutable contracts used to connect the Mini App
to the authoritative shared Ride Platform.

The Mini App is an interface. It must not invent a
separate authoritative ride identity.
"""

from dataclasses import dataclass


def _require_positive_integer(
    value: int,
    *,
    field_name: str,
) -> None:
    """
    Require a real positive integer identifier.

    bool is rejected explicitly because bool is a subclass
    of int in Python.
    """

    if isinstance(value, bool):
        raise ValueError(
            f"{field_name} must be a positive integer."
        )

    if not isinstance(value, int):
        raise ValueError(
            f"{field_name} must be a positive integer."
        )

    if value <= 0:
        raise ValueError(
            f"{field_name} must be a positive integer."
        )


@dataclass(frozen=True)
class MiniAppCanonicalRideReference:
    """
    Immutable reference connecting a Mini App trip
    to one authoritative HABESHAGO ride.

    ride_id is the canonical database ride identity.

    passenger_id and driver_id preserve the actors
    associated with that ride at the integration boundary.
    """

    ride_id: int
    passenger_id: int
    driver_id: int

    def __post_init__(
        self,
    ) -> None:
        _require_positive_integer(
            self.ride_id,
            field_name="ride_id",
        )

        _require_positive_integer(
            self.passenger_id,
            field_name="passenger_id",
        )

        _require_positive_integer(
            self.driver_id,
            field_name="driver_id",
        )