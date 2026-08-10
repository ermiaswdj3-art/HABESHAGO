"""
HABESHAGO Telegram Mini App Authentication

Server-side validation boundary for Telegram Mini App
init data.

Browser-provided Telegram identity is never considered
authoritative until the signed init data has passed
cryptographic verification using HABESHAGO's bot token.

Validated authentication data must also be recent enough
to prevent stale signed Mini App data from being reused.
"""

import hashlib
import hmac
import json
import time

from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl


DEFAULT_MAX_AUTH_AGE_SECONDS = 300
MAX_CLOCK_SKEW_SECONDS = 30


class TelegramInitDataValidationError(ValueError):
    """
    Raised when Telegram Mini App init data cannot be
    trusted.
    """


@dataclass(frozen=True)
class TelegramMiniAppIdentity:
    """
    Authenticated Telegram identity extracted from
    validated Mini App init data.
    """

    telegram_id: int
    first_name: str
    last_name: str | None
    username: str | None
    language_code: str | None
    auth_date: int

    @property
    def full_name(self) -> str:
        """
        Return the normalized Telegram display name.
        """

        parts = (
            self.first_name,
            self.last_name,
        )

        return " ".join(
            part
            for part in parts
            if part
        ).strip()


def _require_bot_token(
    bot_token: Any,
) -> str:
    """
    Require one configured Telegram bot token.
    """

    if (
        not isinstance(
            bot_token,
            str,
        )
        or not bot_token.strip()
    ):
        raise TelegramInitDataValidationError(
            "Telegram bot token is not configured."
        )

    return bot_token.strip()


def _require_init_data(
    init_data: Any,
) -> str:
    """
    Require non-empty Telegram Mini App init data.
    """

    if (
        not isinstance(
            init_data,
            str,
        )
        or not init_data.strip()
    ):
        raise TelegramInitDataValidationError(
            "Telegram init data is required."
        )

    return init_data.strip()


def _require_max_auth_age(
    max_age_seconds: Any,
) -> int:
    """
    Require one positive authentication freshness window.
    """

    if (
        not isinstance(
            max_age_seconds,
            int,
        )
        or isinstance(
            max_age_seconds,
            bool,
        )
        or max_age_seconds <= 0
    ):
        raise TelegramInitDataValidationError(
            "max_age_seconds must be a positive integer."
        )

    return max_age_seconds


def _require_now_timestamp(
    now_timestamp: Any,
) -> int:
    """
    Require one non-negative Unix timestamp.
    """

    if (
        not isinstance(
            now_timestamp,
            int,
        )
        or isinstance(
            now_timestamp,
            bool,
        )
        or now_timestamp < 0
    ):
        raise TelegramInitDataValidationError(
            "now_timestamp must be a non-negative integer."
        )

    return now_timestamp


def _parse_init_data(
    init_data: str,
) -> dict[str, str]:
    """
    Parse Telegram query-string init data while rejecting
    duplicate fields.
    """

    try:
        pairs = parse_qsl(
            init_data,
            keep_blank_values=True,
            strict_parsing=True,
        )

    except ValueError as exc:
        raise TelegramInitDataValidationError(
            "Telegram init data is malformed."
        ) from exc

    parsed: dict[str, str] = {}

    for key, value in pairs:
        if key in parsed:
            raise TelegramInitDataValidationError(
                (
                    "Telegram init data contains "
                    "duplicate fields."
                )
            )

        parsed[key] = value

    return parsed


def _parse_auth_date(
    fields: dict[str, str],
) -> int:
    """
    Load the signed Telegram authentication timestamp.
    """

    raw_auth_date = fields.get(
        "auth_date"
    )

    if not raw_auth_date:
        raise TelegramInitDataValidationError(
            (
                "Telegram init data does not contain "
                "auth_date."
            )
        )

    try:
        auth_date = int(
            raw_auth_date
        )

    except ValueError as exc:
        raise TelegramInitDataValidationError(
            "Telegram auth_date is invalid."
        ) from exc

    if auth_date < 0:
        raise TelegramInitDataValidationError(
            "Telegram auth_date is invalid."
        )

    return auth_date


def _validate_auth_freshness(
    *,
    auth_date: int,
    now_timestamp: int,
    max_age_seconds: int,
) -> None:
    """
    Reject stale authentication data and timestamps that
    are implausibly far in the future.
    """

    age_seconds = (
        now_timestamp
        - auth_date
    )

    if age_seconds < -MAX_CLOCK_SKEW_SECONDS:
        raise TelegramInitDataValidationError(
            (
                "Telegram init data auth_date "
                "is in the future."
            )
        )

    if age_seconds > max_age_seconds:
        raise TelegramInitDataValidationError(
            "Telegram init data has expired."
        )


def validate_telegram_init_data(
    *,
    init_data: str,
    bot_token: str,
    max_age_seconds: int = (
        DEFAULT_MAX_AUTH_AGE_SECONDS
    ),
    now_timestamp: int | None = None,
) -> TelegramMiniAppIdentity:
    """
    Validate Telegram Mini App init data and return the
    authenticated Telegram user identity.

    Validation includes:
    - required input checks;
    - duplicate-field rejection;
    - Telegram HMAC-SHA-256 signature verification;
    - authentication timestamp freshness validation;
    - Telegram user payload validation.

    This function performs no network request.
    """

    trusted_token = _require_bot_token(
        bot_token
    )

    trusted_init_data = _require_init_data(
        init_data
    )

    trusted_max_age = _require_max_auth_age(
        max_age_seconds
    )

    if now_timestamp is None:
        trusted_now = int(
            time.time()
        )
    else:
        trusted_now = (
            _require_now_timestamp(
                now_timestamp
            )
        )

    fields = _parse_init_data(
        trusted_init_data
    )

    received_hash = fields.pop(
        "hash",
        None,
    )

    if not received_hash:
        raise TelegramInitDataValidationError(
            (
                "Telegram init data does not "
                "contain a hash."
            )
        )

    # ==========================================
    # TELEGRAM SIGNATURE VERIFICATION
    # ==========================================

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(
            fields.items()
        )
    )

    secret_key = hmac.new(
        b"WebAppData",
        trusted_token.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        calculated_hash,
        received_hash,
    ):
        raise TelegramInitDataValidationError(
            (
                "Telegram init data signature "
                "is invalid."
            )
        )

    # ==========================================
    # AUTHENTICATION FRESHNESS
    # ==========================================

    auth_date = _parse_auth_date(
        fields
    )

    _validate_auth_freshness(
        auth_date=auth_date,
        now_timestamp=trusted_now,
        max_age_seconds=(
            trusted_max_age
        ),
    )

    # ==========================================
    # AUTHENTICATED TELEGRAM USER
    # ==========================================

    raw_user = fields.get(
        "user"
    )

    if not raw_user:
        raise TelegramInitDataValidationError(
            (
                "Telegram init data does not "
                "contain a user."
            )
        )

    try:
        user = json.loads(
            raw_user
        )

    except json.JSONDecodeError as exc:
        raise TelegramInitDataValidationError(
            "Telegram user data is malformed."
        ) from exc

    if not isinstance(
        user,
        dict,
    ):
        raise TelegramInitDataValidationError(
            (
                "Telegram user data must "
                "be an object."
            )
        )

    telegram_id = user.get(
        "id"
    )

    if (
        not isinstance(
            telegram_id,
            int,
        )
        or isinstance(
            telegram_id,
            bool,
        )
        or telegram_id <= 0
    ):
        raise TelegramInitDataValidationError(
            "Telegram user ID is invalid."
        )

    first_name = user.get(
        "first_name"
    )

    if (
        not isinstance(
            first_name,
            str,
        )
        or not first_name.strip()
    ):
        raise TelegramInitDataValidationError(
            "Telegram first name is invalid."
        )

    last_name = user.get(
        "last_name"
    )

    username = user.get(
        "username"
    )

    language_code = user.get(
        "language_code"
    )

    for field_name, value in (
        (
            "last_name",
            last_name,
        ),
        (
            "username",
            username,
        ),
        (
            "language_code",
            language_code,
        ),
    ):
        if (
            value is not None
            and not isinstance(
                value,
                str,
            )
        ):
            raise TelegramInitDataValidationError(
                (
                    f"Telegram {field_name} "
                    "is invalid."
                )
            )

    return TelegramMiniAppIdentity(
        telegram_id=telegram_id,
        first_name=(
            first_name.strip()
        ),
        last_name=(
            last_name.strip()
            if last_name
            else None
        ),
        username=(
            username.strip()
            if username
            else None
        ),
        language_code=(
            language_code.strip()
            if language_code
            else None
        ),
        auth_date=auth_date,
    )