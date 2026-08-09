"""
HABESHAGO Payment Reconciliation Domain

Turns a verified provider-evidence decision into an
explicit financial reconciliation result.

Verification answers:

    "Does this provider evidence match the authoritative
    HABESHAGO payment transaction?"

Reconciliation answers:

    "What is the current financial relationship between
    HABESHAGO's transaction and the provider evidence?"

Commit #97 does not:
- call providers
- move money
- modify settlement
- mutate pricing
- publish events
"""

from dataclasses import (
    dataclass,
)

from datetime import (
    datetime,
)

from app.payments.exceptions import (
    PaymentReconciliationError,
    PaymentValidationError,
)

from app.payments.models import (
    PaymentTransaction,
)

from app.payments.verification import (
    PaymentVerificationResult,
    PaymentVerificationStatus,
    _require_aware_datetime,
    _require_text,
)


class PaymentReconciliationStatus:
    """
    Canonical reconciliation outcomes.
    """

    RECONCILED = "reconciled"

    PENDING = "pending"

    MISMATCHED = "mismatched"

    FAILED = "failed"

    ALL = {
        RECONCILED,
        PENDING,
        MISMATCHED,
        FAILED,
    }


@dataclass(
    frozen=True,
    slots=True,
)
class PaymentReconciliationResult:
    """
    Immutable financial reconciliation decision.

    A RECONCILED result means the provider evidence was
    verified as matching the authoritative transaction and
    reports a completed provider payment.

    It does not itself perform settlement.
    """

    transaction_reference: str

    provider: str

    provider_reference: str

    status: str

    reconciled_at: datetime

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

        _require_text(
            self.provider,
            field_name="provider",
        )

        _require_text(
            self.provider_reference,
            field_name=(
                "provider_reference"
            ),
        )

        if (
            self.status
            not in PaymentReconciliationStatus.ALL
        ):
            raise PaymentValidationError(
                (
                    "Unsupported reconciliation status: "
                    f"{self.status}"
                )
            )

        _require_aware_datetime(
            self.reconciled_at,
            field_name="reconciled_at",
        )

        if self.reason is not None:
            _require_text(
                self.reason,
                field_name="reason",
            )

        if (
            self.status
            == PaymentReconciliationStatus.RECONCILED
            and self.reason is not None
        ):
            raise PaymentValidationError(
                (
                    "A reconciled payment must not "
                    "contain a failure reason."
                )
            )


def reconcile_payment(
    *,
    transaction: PaymentTransaction,
    verification: PaymentVerificationResult,
    reconciled_at: datetime,
) -> PaymentReconciliationResult:
    """
    Reconcile one authoritative PaymentTransaction using one
    PaymentVerificationResult.

    Only MATCHED verification may become RECONCILED.
    """

    if not isinstance(
        transaction,
        PaymentTransaction,
    ):
        raise PaymentReconciliationError(
            (
                "transaction must be a "
                "PaymentTransaction."
            )
        )

    if not isinstance(
        verification,
        PaymentVerificationResult,
    ):
        raise PaymentReconciliationError(
            (
                "verification must be a "
                "PaymentVerificationResult."
            )
        )

    _require_aware_datetime(
        reconciled_at,
        field_name="reconciled_at",
    )

    if (
        reconciled_at
        < verification.verified_at
    ):
        raise PaymentReconciliationError(
            (
                "reconciled_at cannot be earlier "
                "than verification verified_at."
            )
        )

    if (
        verification.transaction_reference
        != transaction.transaction_reference
    ):
        raise PaymentReconciliationError(
            (
                "Verification transaction reference "
                "does not match the authoritative "
                "PaymentTransaction."
            )
        )

    if (
        verification.provider
        != transaction.provider
    ):
        raise PaymentReconciliationError(
            (
                "Verification provider does not "
                "match the authoritative "
                "PaymentTransaction."
            )
        )

    if (
        transaction.provider_reference
        is not None
        and verification.provider_reference
        != transaction.provider_reference
    ):
        raise PaymentReconciliationError(
            (
                "Verification provider reference does "
                "not match the authoritative "
                "PaymentTransaction."
            )
        )

    if (
        verification.status
        == PaymentVerificationStatus.MATCHED
    ):
        return PaymentReconciliationResult(
            transaction_reference=(
                transaction.transaction_reference
            ),
            provider=transaction.provider,
            provider_reference=(
                verification.provider_reference
            ),
            status=(
                PaymentReconciliationStatus.RECONCILED
            ),
            reconciled_at=reconciled_at,
        )

    if (
        verification.status
        == PaymentVerificationStatus.PENDING
    ):
        status = (
            PaymentReconciliationStatus.PENDING
        )

        reason = (
            verification.reason
            or "Payment verification remains pending."
        )

    elif (
        verification.status
        == PaymentVerificationStatus.MISMATCHED
    ):
        status = (
            PaymentReconciliationStatus.MISMATCHED
        )

        reason = (
            verification.reason
            or "Provider evidence is mismatched."
        )

    else:
        status = (
            PaymentReconciliationStatus.FAILED
        )

        reason = (
            verification.reason
            or "Provider verification failed."
        )

    return PaymentReconciliationResult(
        transaction_reference=(
            transaction.transaction_reference
        ),
        provider=transaction.provider,
        provider_reference=(
            verification.provider_reference
        ),
        status=status,
        reconciled_at=reconciled_at,
        reason=reason,
    )