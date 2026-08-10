"""
HABESHAGO Mini App Authentication

Public authentication boundary for Telegram Mini App
identity verification and canonical HABESHAGO passenger
and driver resolution.
"""

from app.mini_app.auth.authenticated_driver import (
    AuthenticatedMiniAppDriver,
    authenticate_mini_app_driver,
)

from app.mini_app.auth.authenticated_passenger import (
    AuthenticatedMiniAppPassenger,
    authenticate_mini_app_passenger,
)

from app.mini_app.auth.driver_identity import (
    MiniAppDriverIdentity,
    MiniAppDriverIdentityError,
    resolve_authenticated_driver,
)

from app.mini_app.auth.passenger_identity import (
    MiniAppPassengerIdentity,
    MiniAppPassengerIdentityError,
    resolve_authenticated_passenger,
)

from app.mini_app.auth.telegram_init_data import (
    TelegramInitDataValidationError,
    TelegramMiniAppIdentity,
    validate_telegram_init_data,
)


__all__ = [
    "AuthenticatedMiniAppDriver",
    "AuthenticatedMiniAppPassenger",
    "MiniAppDriverIdentity",
    "MiniAppDriverIdentityError",
    "MiniAppPassengerIdentity",
    "MiniAppPassengerIdentityError",
    "TelegramInitDataValidationError",
    "TelegramMiniAppIdentity",
    "authenticate_mini_app_driver",
    "authenticate_mini_app_passenger",
    "resolve_authenticated_driver",
    "resolve_authenticated_passenger",
    "validate_telegram_init_data",
]