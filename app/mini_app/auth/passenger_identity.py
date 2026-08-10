"""
HABESHAGO Mini App Passenger Identity

Resolves one cryptographically authenticated Telegram
Mini App identity into the existing canonical HABESHAGO
passenger record.

The Mini App does not create a competing passenger
identity system.
"""

from dataclasses import dataclass

from app.database.passenger_repository import (
    get_passenger,
    register_passenger,
)

from app.mini_app.auth.telegram_init_data import (
    TelegramMiniAppIdentity,
)


class MiniAppPassengerIdentityError(ValueError):
    """
    Raised when an authenticated Telegram user cannot be
    resolved into a canonical HABESHAGO passenger.
    """


@dataclass(frozen=True)
class MiniAppPassengerIdentity:
    """
    Canonical passenger identity available to the
    authenticated Mini App.
    """

    telegram_id: int
    full_name: str
    phone_number: str | None
    created_at: object


def resolve_authenticated_passenger(
    *,
    identity: TelegramMiniAppIdentity,
    register_if_missing: bool = True,
) -> MiniAppPassengerIdentity:
    """
    Resolve one authenticated Telegram identity into the
    canonical HABESHAGO passengers table.

    When register_if_missing is True, the behavior mirrors
    the Telegram Bot's existing passenger registration
    boundary.
    """

    if not isinstance(
        identity,
        TelegramMiniAppIdentity,
    ):
        raise MiniAppPassengerIdentityError(
            (
                "identity must be a "
                "TelegramMiniAppIdentity."
            )
        )

    passenger = get_passenger(
        identity.telegram_id
    )

    if (
        passenger is None
        and register_if_missing
    ):
        full_name = (
            identity.full_name
            or identity.first_name
        )

        register_passenger(
            telegram_id=(
                identity.telegram_id
            ),
            full_name=full_name,
        )

        passenger = get_passenger(
            identity.telegram_id
        )

    if passenger is None:
        raise MiniAppPassengerIdentityError(
            "Canonical HABESHAGO passenger was not found."
        )

    return MiniAppPassengerIdentity(
        telegram_id=int(
            passenger[0]
        ),
        full_name=str(
            passenger[1]
        ),
        phone_number=(
            str(
                passenger[2]
            )
            if passenger[2] is not None
            else None
        ),
        created_at=passenger[3],
    )