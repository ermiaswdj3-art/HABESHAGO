"""
HABESHAGO Payment Provider Domain

Defines provider-independent execution contracts used by
the Payment Provider Gateway.

Commit #96 establishes execution language only.

A provider execution result records what an adapter
returned. It does not by itself prove final settlement or
reconciliation.
"""

from dataclasses import (
    dataclass,
)

from datetime import (
    datetime,
)

from decimal import (
    Decimal,
)

from app.payments.constants import (
    PaymentCurrency,
    PaymentProvider,
)

from app.payments.exceptions import (
    PaymentValidationError,
)


class PaymentExecutionStatus:
    """
    Canonical result vocabulary returned by provider
    adapters.

    These statuses describe the immediate provider
    execution response, not final reconciliation.
    """

    PENDING = "pending"

    AUTHORIZED = "authorized"

    COMPLETED = "completed"

    FAILED = "failed"

    ALL = {
        PENDING,
        AUTHORIZED,
        COMPLETED,
        FAILED,
    }


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
class PaymentExecutionRequest:
    """
    Immutable provider-independent execution request.

    The adapter receives only the canonical facts required
    to attempt payment execution.
    """

    transaction_reference: str

    provider: str

    amount: Decimal

    currency: str

    payer_id: int

    obligation_reference: str

    requested_at: datetime

    def __post_init__(
        self,
    ) -> None:
        _require_text(
            self.transaction_reference,
            field_name=(
                "transaction_reference"
            ),
        )

        if self.provider not in PaymentProvider.ALL:
            raise PaymentValidationError(
                (
                    "Unsupported provider: "
                    f"{self.provider}"
                )
            )

        if not isinstance(
            self.amount,
            Decimal,
        ):
            raise PaymentValidationError(
                "amount must be Decimal."
            )

        if not self.amount.is_finite():
            raise PaymentValidationError(
                "amount must be finite."
            )

        if self.amount <= Decimal("0"):
            raise PaymentValidationError(
                (
                    "amount must be greater "
                    "than zero."
                )
            )

        if self.currency not in PaymentCurrency.ALL:
            raise PaymentValidationError(
                (
                    "Unsupported currency: "
                    f"{self.currency}"
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

        _require_text(
            self.obligation_reference,
            field_name=(
                "obligation_reference"
            ),
        )

        _require_aware_datetime(
            self.requested_at,
            field_name="requested_at",
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PaymentExecutionResult:
    """
    Immutable canonical result returned by one provider
    adapter.

    provider_reference is optional because some adapters
    may return an asynchronous result before assigning one.

    A completed result still requires later verification
    and reconciliation before HABESHAGO treats the payment
    as financially final.
    """

    transaction_reference: str

    provider: str

    status: str

    processed_at: datetime

    provider_reference: str | None = None

    failure_reason: str | None = None

    def __post_init__(
        self,
    ) -> None:
        _require_text(
            self.transaction_reference,
            field_name=(
                "transaction_reference"
            ),
        )

        if self.provider not in PaymentProvider.ALL:
            raise PaymentValidationError(
                (
                    "Unsupported provider: "
                    f"{self.provider}"
                )
            )

        if (
            self.status
            not in PaymentExecutionStatus.ALL
        ):
            raise PaymentValidationError(
                (
                    "Unsupported execution status: "
                    f"{self.status}"
                )
            )

        _require_aware_datetime(
            self.processed_at,
            field_name="processed_at",
        )

        if self.provider_reference is not None:
            _require_text(
                self.provider_reference,
                field_name=(
                    "provider_reference"
                ),
            )

        if self.failure_reason is not None:
            _require_text(
                self.failure_reason,
                field_name="failure_reason",
            )

        if (
            self.status
            == PaymentExecutionStatus.FAILED
            and self.failure_reason is None
        ):
            raise PaymentValidationError(
                (
                    "A failed payment execution "
                    "requires failure_reason."
                )
            )

        if (
            self.status
            != PaymentExecutionStatus.FAILED
            and self.failure_reason is not None
        ):
            raise PaymentValidationError(
                (
                    "failure_reason is allowed only "
                    "for failed payment execution."
                )
            )