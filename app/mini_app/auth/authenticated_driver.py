"""
HABESHAGO Authenticated Mini App Driver

Combines Telegram Mini App cryptographic verification
with canonical HABESHAGO driver resolution.

This is the public trust boundary used before the Mini App
may perform authoritative driver operations such as
accepting a shared Ride Offer.

Telegram authentication proves identity.

Canonical HABESHAGO driver registration determines whether
the authenticated user is a registered driver and whether
that driver is authorized to operate.
"""

from dataclasses import dataclass

from app.mini_app.auth.driver_identity import (
    MiniAppDriverIdentity,
    resolve_authenticated_driver,
)

from app.mini_app.auth.telegram_init_data import (
    TelegramMiniAppIdentity,
    validate_telegram_init_data,
)


@dataclass(frozen=True)
class AuthenticatedMiniAppDriver:
    """
    Authenticated Mini App driver context.
    """

    telegram_identity: TelegramMiniAppIdentity
    driver: MiniAppDriverIdentity

    @property
    def driver_id(self) -> int:
        """
        Return the canonical HABESHAGO driver identity.
        """

        return self.driver.driver_id

    @property
    def telegram_id(self) -> int:
        """
        Return the authenticated Telegram identity.
        """

        return self.telegram_identity.telegram_id

    @property
    def can_operate(self) -> bool:
        """
        Return whether the canonical driver is currently
        authorized to perform driver operations.
        """

        return self.driver.can_operate


def authenticate_mini_app_driver(
    *,
    init_data: str,
    bot_token: str,
    require_operational: bool = True,
    max_age_seconds: int = 300,
    now_timestamp: int | None = None,
) -> AuthenticatedMiniAppDriver:
    """
    Authenticate Telegram Mini App init data and resolve
    the corresponding canonical HABESHAGO driver.

    The browser never supplies driver_id directly.
    """

    telegram_identity = (
        validate_telegram_init_data(
            init_data=init_data,
            bot_token=bot_token,
            max_age_seconds=max_age_seconds,
            now_timestamp=now_timestamp,
        )
    )

    driver = (
        resolve_authenticated_driver(
            identity=telegram_identity,
            require_operational=require_operational,
        )
    )

    if (
        driver.driver_id
        != telegram_identity.telegram_id
    ):
        raise ValueError(
            (
                "Authenticated Telegram identity does "
                "not match the canonical HABESHAGO "
                "driver."
            )
        )

    return AuthenticatedMiniAppDriver(
        telegram_identity=telegram_identity,
        driver=driver,
    )