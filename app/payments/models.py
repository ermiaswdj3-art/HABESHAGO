"""
HABESHAGO Payment Platform Models

Defines immutable canonical payment-domain contracts.

Commit #93 establishes payment language and validation only.

This module does not:
- process payments
- contact payment providers
- generate provider confirmations
- move money
- persist transactions
- perform reconciliation
"""

from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from decimal import (
    Decimal,
)

from uuid import (
    uuid4,
)

from app.payments.constants import (
    PaymentCurrency,
    PaymentMethod,
    PaymentSource,
    PaymentStatus,
)

from app.payments.exceptions import (
    PaymentValidationError,
)

from app.payments.versions import (
    PAYMENT_CONTRACT_VERSION,
)


ZERO_MONEY = Decimal("0.00")


def _require_text(
    value,
    *,
    field_name: str,
) -> str:
    """
    Require one non-empty string.
    """

    if not isinstance(
        value,
        str,
    ):
        raise PaymentValidationError(
            f"{field_name} must be str."
        )

    normalized = value.strip()

    if not normalized:
        raise PaymentValidationError(
            f"{field_name} cannot be empty."
        )

    return normalized


def _require_choice(
    value,
    *,
    field_name: str,
    allowed_values: set[str],
) -> str:
    """
    Require one canonical vocabulary value.
    """

    normalized = _require_text(
        value,
        field_name=field_name,
    )

    if normalized not in allowed_values:
        raise PaymentValidationError(
            (
                f"Unsupported {field_name}: "
                f"{normalized}"
            )
        )

    return normalized


def _require_decimal(
    value,
    *,
    field_name: str,
    allow_zero: bool = True,
) -> Decimal:
    """
    Require one finite non-negative exact Decimal.
    """

    if not isinstance(
        value,
        Decimal,
    ):
        raise PaymentValidationError(
            f"{field_name} must be Decimal."
        )

    if not value.is_finite():
        raise PaymentValidationError(
            f"{field_name} must be finite."
        )

    if value < ZERO_MONEY:
        raise PaymentValidationError(
            f"{field_name} cannot be negative."
        )

    if (
        not allow_zero
        and value == ZERO_MONEY
    ):
        raise PaymentValidationError(
            f"{field_name} must be greater than zero."
        )

    return value


def _require_aware_datetime(
    value,
    *,
    field_name: str,
) -> datetime:
    """
    Require one timezone-aware datetime.
    """

    if not isinstance(
        value,
        datetime,
    ):
        raise PaymentValidationError(
            f"{field_name} must be datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PaymentValidationError(
            (
                f"{field_name} must be "
                "timezone-aware."
            )
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class PaymentObligation:
    """
    Immutable financial obligation requiring payment.

    The amount represents what the payer owes.

    Pricing determines this obligation.

    Payment fulfills it.

    Settlement later distributes the received financial
    value.
    """

    obligation_reference: str

    source_type: str

    source_reference: str

    amount: Decimal

    currency: str = PaymentCurrency.ETB

    pricing_quote_id: str | None = None

    pricing_request_id: str | None = None

    created_at: datetime = field(
        default_factory=lambda: (
            datetime.now(
                timezone.utc
            )
        )
    )

    contract_version: str = (
        PAYMENT_CONTRACT_VERSION
    )

    def __post_init__(
        self,
    ) -> None:
        _require_text(
            self.obligation_reference,
            field_name=(
                "obligation_reference"
            ),
        )

        _require_choice(
            self.source_type,
            field_name="source_type",
            allowed_values=(
                PaymentSource.ALL
            ),
        )

        _require_text(
            self.source_reference,
            field_name=(
                "source_reference"
            ),
        )

        _require_decimal(
            self.amount,
            field_name="amount",
            allow_zero=False,
        )

        _require_choice(
            self.currency,
            field_name="currency",
            allowed_values=(
                PaymentCurrency.ALL
            ),
        )

        if self.pricing_quote_id is not None:
            _require_text(
                self.pricing_quote_id,
                field_name=(
                    "pricing_quote_id"
                ),
            )

        if self.pricing_request_id is not None:
            _require_text(
                self.pricing_request_id,
                field_name=(
                    "pricing_request_id"
                ),
            )

        _require_aware_datetime(
            self.created_at,
            field_name="created_at",
        )

        _require_text(
            self.contract_version,
            field_name="contract_version",
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PaymentRequest:
    """
    Immutable request to begin fulfilling one payment
    obligation.
    """

    obligation: PaymentObligation

    payer_id: int

    payment_method: str

    request_reference: str = field(
        default_factory=lambda: (
            f"PAYREQ-{uuid4()}"
        )
    )

    status: str = PaymentStatus.CREATED

    requested_at: datetime = field(
        default_factory=lambda: (
            datetime.now(
                timezone.utc
            )
        )
    )

    contract_version: str = (
        PAYMENT_CONTRACT_VERSION
    )

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.obligation,
            PaymentObligation,
        ):
            raise PaymentValidationError(
                (
                    "obligation must be a "
                    "PaymentObligation."
                )
            )

        if (
            not isinstance(
                self.payer_id,
                int,
            )
            or isinstance(
                self.payer_id,
                bool,
            )
            or self.payer_id <= 0
        ):
            raise PaymentValidationError(
                (
                    "payer_id must be a positive "
                    "integer."
                )
            )

        _require_choice(
            self.payment_method,
            field_name="payment_method",
            allowed_values=(
                PaymentMethod.ALL
            ),
        )

        _require_text(
            self.request_reference,
            field_name="request_reference",
        )

        _require_choice(
            self.status,
            field_name="status",
            allowed_values=(
                PaymentStatus.ALL
            ),
        )

        if self.status != PaymentStatus.CREATED:
            raise PaymentValidationError(
                (
                    "A new PaymentRequest must start "
                    "with status created."
                )
            )

        _require_aware_datetime(
            self.requested_at,
            field_name="requested_at",
        )

        _require_text(
            self.contract_version,
            field_name="contract_version",
        )