"""
HABESHAGO Payment Verification Domain

Defines immutable provider-verification evidence and
verification results.

Commit #97 separates provider evidence from HABESHAGO's
authoritative PaymentTransaction.

Provider evidence never becomes financial truth merely
because a provider reports success.

Verification compares provider evidence against the
authoritative HABESHAGO transaction.

This module does not:
- call external providers
- mutate transactions
- persist verification records
- reconcile settlement
- publish events
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


class ProviderPaymentStatus:
    """
    Canonical status vocabulary observed from provider
    verification evidence.

    Provider-specific adapters will later map their native
    status vocabulary into these canonical values.
    """

    PENDING = "pending"

    AUTHORIZED = "authorized"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    EXPIRED = "expired"

    REFUNDED = "refunded"

    ALL = {
        PENDING,
        AUTHORIZED,
        COMPLETED,
        FAILED,
        CANCELLED,
        EXPIRED,
        REFUNDED,
    }


class PaymentVerificationStatus:
    """
    Canonical HABESHAGO verification outcome.
    """

    MATCHED = "matched"

    PENDING = "pending"

    MISMATCHED = "mismatched"

    FAILED = "failed"

    ALL = {
        MATCHED,
        PENDING,
        MISMATCHED,
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


def _require_decimal(
    value,
    *,
    field_name: str,
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

    if value < Decimal("0"):
        raise PaymentValidationError(
            f"{field_name} cannot be negative."
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
class ProviderVerificationEvidence:
    """
    Immutable canonical evidence observed from one payment
    provider.

    provider_reference identifies the provider-side
    transaction or payment record being verified.

    amount and currency represent what the provider says
    was processed.

    provider_status is mapped from provider-specific status
    vocabulary into HABESHAGO's canonical vocabulary.

    Evidence is not itself a verification decision.
    """

    transaction_reference: str

    provider: str

    provider_reference: str

    amount: Decimal

    currency: str

    provider_status: str

    observed_at: datetime

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

        _require_text(
            self.provider_reference,
            field_name=(
                "provider_reference"
            ),
        )

        _require_decimal(
            self.amount,
            field_name="amount",
        )

        if self.currency not in PaymentCurrency.ALL:
            raise PaymentValidationError(
                (
                    "Unsupported currency: "
                    f"{self.currency}"
                )
            )

        if (
            self.provider_status
            not in ProviderPaymentStatus.ALL
        ):
            raise PaymentValidationError(
                (
                    "Unsupported provider_status: "
                    f"{self.provider_status}"
                )
            )

        _require_aware_datetime(
            self.observed_at,
            field_name="observed_at",
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PaymentVerificationResult:
    """
    Immutable result of verifying provider evidence against
    one authoritative HABESHAGO PaymentTransaction.

    matched_fields and mismatched_fields make the decision
    auditable without parsing human-readable text.
    """

    transaction_reference: str

    provider: str

    provider_reference: str

    status: str

    verified_at: datetime

    matched_fields: tuple[
        str,
        ...,
    ] = ()

    mismatched_fields: tuple[
        str,
        ...,
    ] = ()

    reason: str | None = None

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

        _require_text(
            self.provider_reference,
            field_name=(
                "provider_reference"
            ),
        )

        if (
            self.status
            not in PaymentVerificationStatus.ALL
        ):
            raise PaymentValidationError(
                (
                    "Unsupported verification status: "
                    f"{self.status}"
                )
            )

        _require_aware_datetime(
            self.verified_at,
            field_name="verified_at",
        )

        if not isinstance(
            self.matched_fields,
            tuple,
        ):
            raise PaymentValidationError(
                (
                    "matched_fields must be "
                    "a tuple."
                )
            )

        if not isinstance(
            self.mismatched_fields,
            tuple,
        ):
            raise PaymentValidationError(
                (
                    "mismatched_fields must be "
                    "a tuple."
                )
            )

        for field_name in self.matched_fields:
            _require_text(
                field_name,
                field_name=(
                    "matched_fields value"
                ),
            )

        for field_name in self.mismatched_fields:
            _require_text(
                field_name,
                field_name=(
                    "mismatched_fields value"
                ),
            )

        if self.reason is not None:
            _require_text(
                self.reason,
                field_name="reason",
            )

        if (
            self.status
            == PaymentVerificationStatus.MATCHED
            and self.mismatched_fields
        ):
            raise PaymentValidationError(
                (
                    "A matched verification cannot "
                    "contain mismatched_fields."
                )
            )

        if (
            self.status
            == PaymentVerificationStatus.MISMATCHED
            and not self.mismatched_fields
        ):
            raise PaymentValidationError(
                (
                    "A mismatched verification "
                    "requires mismatched_fields."
                )
            )

def verify_payment_evidence(
    *,
    transaction,
    evidence: ProviderVerificationEvidence,
    verified_at: datetime,
) -> PaymentVerificationResult:
    """
    Verify provider evidence against one authoritative
    PaymentTransaction.

    Verification checks:
    - transaction reference
    - provider
    - provider reference consistency when already known
    - exact Decimal amount
    - currency
    - provider payment state

    A provider COMPLETED state becomes MATCHED only when all
    authoritative financial identity checks match.
    """

    from app.payments.models import (
        PaymentTransaction,
    )

    if not isinstance(
        transaction,
        PaymentTransaction,
    ):
        raise PaymentValidationError(
            (
                "transaction must be a "
                "PaymentTransaction."
            )
        )

    if not isinstance(
        evidence,
        ProviderVerificationEvidence,
    ):
        raise PaymentValidationError(
            (
                "evidence must be "
                "ProviderVerificationEvidence."
            )
        )

    _require_aware_datetime(
        verified_at,
        field_name="verified_at",
    )

    if verified_at < transaction.created_at:
        raise PaymentValidationError(
            (
                "verified_at cannot be earlier "
                "than PaymentTransaction created_at."
            )
        )

    if verified_at < evidence.observed_at:
        raise PaymentValidationError(
            (
                "verified_at cannot be earlier "
                "than evidence observed_at."
            )
        )

    matched_fields = []

    mismatched_fields = []

    if (
        evidence.transaction_reference
        == transaction.transaction_reference
    ):
        matched_fields.append(
            "transaction_reference"
        )
    else:
        mismatched_fields.append(
            "transaction_reference"
        )

    if evidence.provider == transaction.provider:
        matched_fields.append(
            "provider"
        )
    else:
        mismatched_fields.append(
            "provider"
        )

    if evidence.amount == transaction.amount:
        matched_fields.append(
            "amount"
        )
    else:
        mismatched_fields.append(
            "amount"
        )

    if evidence.currency == transaction.currency:
        matched_fields.append(
            "currency"
        )
    else:
        mismatched_fields.append(
            "currency"
        )

    if transaction.provider_reference is None:
        matched_fields.append(
            "provider_reference"
        )

    elif (
        evidence.provider_reference
        == transaction.provider_reference
    ):
        matched_fields.append(
            "provider_reference"
        )

    else:
        mismatched_fields.append(
            "provider_reference"
        )

    if mismatched_fields:
        return PaymentVerificationResult(
            transaction_reference=(
                transaction.transaction_reference
            ),
            provider=transaction.provider,
            provider_reference=(
                evidence.provider_reference
            ),
            status=(
                PaymentVerificationStatus.MISMATCHED
            ),
            verified_at=verified_at,
            matched_fields=tuple(
                matched_fields
            ),
            mismatched_fields=tuple(
                mismatched_fields
            ),
            reason=(
                "Provider evidence does not match "
                "authoritative payment facts."
            ),
        )

    if (
        evidence.provider_status
        == ProviderPaymentStatus.COMPLETED
    ):
        status = (
            PaymentVerificationStatus.MATCHED
        )

        reason = None

    elif (
        evidence.provider_status
        in {
            ProviderPaymentStatus.PENDING,
            ProviderPaymentStatus.AUTHORIZED,
        }
    ):
        status = (
            PaymentVerificationStatus.PENDING
        )

        reason = (
            "Provider payment is not yet final."
        )

    else:
        status = (
            PaymentVerificationStatus.FAILED
        )

        reason = (
            "Provider reports a non-successful "
            "terminal payment state."
        )

    return PaymentVerificationResult(
        transaction_reference=(
            transaction.transaction_reference
        ),
        provider=transaction.provider,
        provider_reference=(
            evidence.provider_reference
        ),
        status=status,
        verified_at=verified_at,
        matched_fields=tuple(
            matched_fields
        ),
        mismatched_fields=(),
        reason=reason,
    )