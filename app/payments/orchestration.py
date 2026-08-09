"""
HABESHAGO Payment Orchestration Domain

Defines immutable contracts describing the outcome of one
coordinated Payment Platform workflow.

Commit #99 coordinates the existing Payment Platform built
across Commits #93 through #98.

This domain does not:
- calculate pricing
- execute provider APIs
- persist records
- verify evidence
- reconcile payments
- publish events

Those responsibilities remain owned by their existing
platform services.
"""

from dataclasses import (
    dataclass,
)

from app.models.event import (
    Event,
)

from app.payments.models import (
    PaymentIntent,
    PaymentObligation,
    PaymentRequest,
    PaymentTransaction,
)

from app.payments.provider import (
    PaymentExecutionResult,
)

from app.payments.reconciliation import (
    PaymentReconciliationResult,
)

from app.payments.verification import (
    PaymentVerificationResult,
)


class PaymentWorkflowStatus:
    """
    Canonical Payment Orchestration workflow outcomes.
    """

    PREPARED = "prepared"

    EXECUTION_PENDING = "execution_pending"

    EXECUTION_FAILED = "execution_failed"

    VERIFICATION_PENDING = "verification_pending"

    VERIFICATION_FAILED = "verification_failed"

    RECONCILED = "reconciled"

    ALL = {
        PREPARED,
        EXECUTION_PENDING,
        EXECUTION_FAILED,
        VERIFICATION_PENDING,
        VERIFICATION_FAILED,
        RECONCILED,
    }


@dataclass(
    frozen=True,
    slots=True,
)
class PaymentOrchestrationResult:
    """
    Immutable result of one coordinated Payment Platform
    workflow.

    The result preserves every authoritative object that
    was successfully produced.

    Optional later-stage values remain None when the
    workflow legitimately stops at an earlier stage.

    published_events contains only events that were
    actually published.
    """

    obligation: PaymentObligation

    payment_request: PaymentRequest

    intent: PaymentIntent

    transaction: PaymentTransaction

    status: str

    execution_result: (
        PaymentExecutionResult
        | None
    ) = None

    verification_result: (
        PaymentVerificationResult
        | None
    ) = None

    reconciliation_result: (
        PaymentReconciliationResult
        | None
    ) = None

    published_events: tuple[
        Event,
        ...,
    ] = ()

    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.obligation,
            PaymentObligation,
        ):
            raise ValueError(
                (
                    "obligation must be a "
                    "PaymentObligation."
                )
            )

        if not isinstance(
            self.payment_request,
            PaymentRequest,
        ):
            raise ValueError(
                (
                    "payment_request must be a "
                    "PaymentRequest."
                )
            )

        if not isinstance(
            self.intent,
            PaymentIntent,
        ):
            raise ValueError(
                (
                    "intent must be a "
                    "PaymentIntent."
                )
            )

        if not isinstance(
            self.transaction,
            PaymentTransaction,
        ):
            raise ValueError(
                (
                    "transaction must be a "
                    "PaymentTransaction."
                )
            )

        if (
            self.status
            not in PaymentWorkflowStatus.ALL
        ):
            raise ValueError(
                (
                    "Unsupported payment workflow "
                    f"status: {self.status}"
                )
            )

        if (
            self.execution_result is not None
            and not isinstance(
                self.execution_result,
                PaymentExecutionResult,
            )
        ):
            raise ValueError(
                (
                    "execution_result must be a "
                    "PaymentExecutionResult or None."
                )
            )

        if (
            self.verification_result is not None
            and not isinstance(
                self.verification_result,
                PaymentVerificationResult,
            )
        ):
            raise ValueError(
                (
                    "verification_result must be a "
                    "PaymentVerificationResult or None."
                )
            )

        if (
            self.reconciliation_result is not None
            and not isinstance(
                self.reconciliation_result,
                PaymentReconciliationResult,
            )
        ):
            raise ValueError(
                (
                    "reconciliation_result must be a "
                    "PaymentReconciliationResult or None."
                )
            )

        if not isinstance(
            self.published_events,
            tuple,
        ):
            raise ValueError(
                "published_events must be a tuple."
            )

        for event in self.published_events:
            if not isinstance(
                event,
                Event,
            ):
                raise ValueError(
                    (
                        "published_events must contain "
                        "Event values."
                    )
                )

        # ======================================
        # AUTHORITATIVE OBJECT LINKAGE
        # ======================================

        if (
            self.payment_request.obligation
            != self.obligation
        ):
            raise ValueError(
                (
                    "payment_request must reference "
                    "the orchestration obligation."
                )
            )

        if (
            self.intent.payment_request
            != self.payment_request
        ):
            raise ValueError(
                (
                    "intent must reference the "
                    "orchestration payment_request."
                )
            )

        if (
            self.transaction.intent_reference
            != self.intent.intent_reference
        ):
            raise ValueError(
                (
                    "transaction must reference the "
                    "orchestration intent."
                )
            )

        if (
            self.transaction.obligation_reference
            != self.obligation.obligation_reference
        ):
            raise ValueError(
                (
                    "transaction must reference the "
                    "orchestration obligation."
                )
            )

        # ======================================
        # LATER-STAGE LINKAGE
        # ======================================

        if self.execution_result is not None:
            if (
                self.execution_result
                .transaction_reference
                != self.transaction
                .transaction_reference
            ):
                raise ValueError(
                    (
                        "execution_result must reference "
                        "the orchestration transaction."
                    )
                )

            if (
                self.execution_result.provider
                != self.transaction.provider
            ):
                raise ValueError(
                    (
                        "execution_result provider must "
                        "match the transaction provider."
                    )
                )

        if self.verification_result is not None:
            if (
                self.verification_result
                .transaction_reference
                != self.transaction
                .transaction_reference
            ):
                raise ValueError(
                    (
                        "verification_result must "
                        "reference the orchestration "
                        "transaction."
                    )
                )

        if self.reconciliation_result is not None:
            if (
                self.reconciliation_result
                .transaction_reference
                != self.transaction
                .transaction_reference
            ):
                raise ValueError(
                    (
                        "reconciliation_result must "
                        "reference the orchestration "
                        "transaction."
                    )
                )

        # ======================================
        # WORKFLOW STATUS INVARIANTS
        # ======================================

        if (
            self.status
            == PaymentWorkflowStatus.PREPARED
            and (
                self.execution_result is not None
                or self.verification_result is not None
                or self.reconciliation_result is not None
            )
        ):
            raise ValueError(
                (
                    "A prepared workflow cannot contain "
                    "execution, verification or "
                    "reconciliation results."
                )
            )

        if (
            self.status
            == PaymentWorkflowStatus.RECONCILED
            and self.reconciliation_result is None
        ):
            raise ValueError(
                (
                    "A reconciled workflow requires a "
                    "reconciliation_result."
                )
            )