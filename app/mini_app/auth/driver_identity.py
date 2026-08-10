"""
HABESHAGO Mini App Driver Identity

Resolves one cryptographically authenticated Telegram
Mini App identity into the existing canonical HABESHAGO
driver registration.

The Mini App does not create drivers and does not maintain
a competing driver identity system.

Telegram authentication proves who the user is.

The canonical HABESHAGO driver registration determines
whether that authenticated user is a registered driver and
whether the driver is authorized to perform driver
operations.
"""

from dataclasses import dataclass

from app.mini_app.auth.telegram_init_data import (
    TelegramMiniAppIdentity,
)

from app.services.driver_registration_service import (
    get_driver_registration_status,
)


class MiniAppDriverIdentityError(ValueError):
    """
    Raised when an authenticated Telegram user cannot be
    resolved into a canonical HABESHAGO driver.
    """


@dataclass(frozen=True)
class MiniAppDriverIdentity:
    """
    Canonical driver identity available to the
    authenticated Mini App.
    """

    driver_id: int
    full_name: str
    phone_number: str | None

    registration_status: str
    identity_verification_status: str
    vehicle_verification_status: str

    can_operate: bool

    @property
    def telegram_id(self) -> int:
        """
        Return the Telegram-backed canonical driver ID.

        HABESHAGO currently uses Telegram ID as the shared
        driver identifier across the ride platform.
        """

        return self.driver_id


def resolve_authenticated_driver(
    *,
    identity: TelegramMiniAppIdentity,
    require_operational: bool = False,
) -> MiniAppDriverIdentity:
    """
    Resolve one authenticated Telegram identity into the
    canonical HABESHAGO driver registration.

    This function never creates a driver registration.

    A valid Telegram identity proves identity only.
    HABESHAGO driver authorization remains controlled by
    the canonical registration and verification platform.

    When require_operational is True, only a driver whose
    canonical registration currently permits operation is
    accepted.
    """

    if not isinstance(
        identity,
        TelegramMiniAppIdentity,
    ):
        raise MiniAppDriverIdentityError(
            (
                "identity must be a "
                "TelegramMiniAppIdentity."
            )
        )

    registration = (
        get_driver_registration_status(
            identity.telegram_id
        )
    )

    if registration is None:
        raise MiniAppDriverIdentityError(
            (
                "Authenticated Telegram user is not "
                "registered as a HABESHAGO driver."
            )
        )

    driver_id = registration.get(
        "driver_id"
    )

    if (
        not isinstance(driver_id, int)
        or isinstance(driver_id, bool)
        or driver_id <= 0
    ):
        raise MiniAppDriverIdentityError(
            "Canonical HABESHAGO driver ID is invalid."
        )

    if driver_id != identity.telegram_id:
        raise MiniAppDriverIdentityError(
            (
                "Authenticated Telegram identity does "
                "not match the canonical driver."
            )
        )

    profile = registration.get(
        "profile",
        {},
    )

    verification = registration.get(
        "verification",
        {},
    )

    registration_context = registration.get(
        "registration",
        {},
    )

    registration_status = (
        registration_context.get(
            "status",
            "verification_pending",
        )
    )

    identity_status = verification.get(
        "identity",
        "pending",
    )

    vehicle_status = verification.get(
        "vehicle",
        "pending",
    )

    can_operate = (
        registration.get(
            "can_operate"
        )
        is True
    )

    if (
        require_operational
        and not can_operate
    ):
        raise MiniAppDriverIdentityError(
            (
                "HABESHAGO driver is not authorized "
                "to perform driver operations."
            )
        )

    return MiniAppDriverIdentity(
        driver_id=driver_id,
        full_name=str(
            profile.get(
                "full_name",
                "",
            )
        ),
        phone_number=(
            str(profile["phone_number"])
            if profile.get(
                "phone_number"
            ) is not None
            else None
        ),
        registration_status=str(
            registration_status
        ),
        identity_verification_status=str(
            identity_status
        ),
        vehicle_verification_status=str(
            vehicle_status
        ),
        can_operate=can_operate,
    )