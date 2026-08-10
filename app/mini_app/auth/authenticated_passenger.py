"""
HABESHAGO Authenticated Mini App Passenger

Combines Telegram Mini App cryptographic verification
with canonical HABESHAGO passenger resolution.

This is the public trust boundary used before the Mini App
may perform authoritative passenger operations such as
creating a shared Ride Offer.
"""

from dataclasses import dataclass

from app.mini_app.auth.passenger_identity import (
    MiniAppPassengerIdentity,
    resolve_authenticated_passenger,
)

from app.mini_app.auth.telegram_init_data import (
    TelegramMiniAppIdentity,
    validate_telegram_init_data,
)


@dataclass(frozen=True)
class AuthenticatedMiniAppPassenger:
    """
    Authenticated Mini App passenger context.
    """

    telegram_identity: TelegramMiniAppIdentity
    passenger: MiniAppPassengerIdentity

    @property
    def passenger_id(self) -> int:
        """
        Return the canonical HABESHAGO passenger identity.

        HABESHAGO currently uses Telegram ID as the shared
        passenger identifier across the ride platform.
        """

        return self.passenger.telegram_id

    @property
    def telegram_id(self) -> int:
        """
        Return the authenticated Telegram identity.
        """

        return self.telegram_identity.telegram_id


def authenticate_mini_app_passenger(
    *,
    init_data: str,
    bot_token: str,
    register_if_missing: bool = True,
    max_age_seconds: int = 300,
    now_timestamp: int | None = None,
) -> AuthenticatedMiniAppPassenger:
    """
    Authenticate Telegram Mini App init data and resolve
    the corresponding canonical HABESHAGO passenger.

    The browser never supplies passenger_id directly.
    """

    telegram_identity = (
        validate_telegram_init_data(
            init_data=init_data,
            bot_token=bot_token,
            max_age_seconds=max_age_seconds,
            now_timestamp=now_timestamp,
        )
    )

    passenger = (
        resolve_authenticated_passenger(
            identity=telegram_identity,
            register_if_missing=(
                register_if_missing
            ),
        )
    )

    if (
        passenger.telegram_id
        != telegram_identity.telegram_id
    ):
        raise ValueError(
            (
                "Authenticated Telegram identity does "
                "not match the canonical HABESHAGO "
                "passenger."
            )
        )

    return AuthenticatedMiniAppPassenger(
        telegram_identity=telegram_identity,
        passenger=passenger,
    )