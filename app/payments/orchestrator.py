"""
HABESHAGO Payment Orchestrator

Coordinates authoritative Payment Platform operations
across the domain, persistence, execution, verification,
reconciliation and event layers.

Commit #99 introduces production-oriented orchestration
without moving responsibilities out of their existing
platform services.

The orchestrator coordinates existing capabilities.

It does not:
- calculate pricing;
- implement provider-specific APIs;
- bypass repository boundaries;
- manufacture successful provider responses;
- verify provider evidence itself;
- reconcile financial evidence itself.
"""

from datetime import (
    datetime,
)

from app.database.payment_repository import (
    save_payment_intent,
    save_payment_obligation,
    save_payment_request,
    save_payment_transaction,
)

from app.database.payment_reconciliation_repository import (
    save_payment_reconciliation,
    save_payment_verification,
)

from app.payments.reconciliation import (
    reconcile_payment,
)

from app.payments.verification import (
    PaymentVerificationStatus,
    ProviderVerificationEvidence,
    verify_payment_evidence,
)

from app.payments.intent_service import (
    create_payment_intent,
    create_payment_transaction,
)

from app.payments.models import (
    PaymentObligation,
    PaymentRequest,
)

from app.payments.execution_engine import (
    execute_payment_transaction,
)


from app.payments.orchestration import (
    PaymentOrchestrationResult,
    PaymentWorkflowStatus,
)

from app.payments.execution_engine import (
    execute_payment_transaction,
)

from app.services.payment_event_service import (
    publish_payment_execution_recorded_event,
    publish_payment_reconciled_event,
    publish_payment_transaction_created_event,
    publish_payment_verified_event,
)


def prepare_payment(
    *,
    obligation: PaymentObligation,
    payment_request: PaymentRequest,
    intent_reference: str,
    transaction_reference: str,
    created_at: datetime,
    expires_at: datetime | None = None,
) -> PaymentOrchestrationResult:
    """
    Prepare one durable canonical payment workflow.

    Processing order:

    1. Validate the supplied authoritative obligation and
       payment request relationship.
    2. Persist the PaymentObligation.
    3. Persist the PaymentRequest.
    4. Create and persist the PaymentIntent.
    5. Create and persist the PaymentTransaction.
    6. Publish PAYMENT_TRANSACTION_CREATED.
    7. Return an immutable PREPARED orchestration result.

    Provider execution does not occur here.
    """

    if not isinstance(
        obligation,
        PaymentObligation,
    ):
        raise ValueError(
            (
                "obligation must be a "
                "PaymentObligation."
            )
        )

    if not isinstance(
        payment_request,
        PaymentRequest,
    ):
        raise ValueError(
            (
                "payment_request must be a "
                "PaymentRequest."
            )
        )

    if (
        payment_request.obligation
        != obligation
    ):
        raise ValueError(
            (
                "payment_request must reference "
                "the supplied obligation."
            )
        )

    # ==========================================
    # AUTHORITATIVE PERSISTENCE
    # ==========================================

    persisted_obligation = (
        save_payment_obligation(
            obligation
        )
    )

    persisted_request = (
        save_payment_request(
            payment_request
        )
    )

    # ==========================================
    # PAYMENT INTENT
    # ==========================================

    intent = create_payment_intent(
        payment_request=persisted_request,
        intent_reference=intent_reference,
        created_at=created_at,
        expires_at=expires_at,
    )

    persisted_intent = (
        save_payment_intent(
            intent
        )
    )

    # ==========================================
    # PAYMENT TRANSACTION
    # ==========================================

    transaction = (
        create_payment_transaction(
            intent=persisted_intent,
            transaction_reference=(
                transaction_reference
            ),
            created_at=created_at,
        )
    )

    persisted_transaction = (
        save_payment_transaction(
            transaction
        )
    )

    # ==========================================
    # PLATFORM EVENT
    # ==========================================

    transaction_event = (
        publish_payment_transaction_created_event(
            persisted_transaction
        )
    )

    # ==========================================
    # ORCHESTRATION RESULT
    # ==========================================

    return PaymentOrchestrationResult(
        obligation=persisted_obligation,
        payment_request=persisted_request,
        intent=persisted_intent,
        transaction=persisted_transaction,
        status=PaymentWorkflowStatus.PREPARED,
        published_events=(
            transaction_event,
        ),
    )

def execute_prepared_payment(
    *,
    prepared_result: PaymentOrchestrationResult,
    processed_at: datetime,
) -> PaymentOrchestrationResult:
    """
    Execute one previously prepared Payment Platform
    workflow.

    The workflow must already be PREPARED.

    Provider execution remains entirely owned by the
    Payment Execution Engine.

    If provider execution raises, this function does not:
    - manufacture an execution result;
    - publish a false execution event;
    - advance verification;
    - advance reconciliation.

    Successful execution results are published and
    preserved in a new immutable orchestration result.
    """

    if not isinstance(
        prepared_result,
        PaymentOrchestrationResult,
    ):
        raise ValueError(
            (
                "prepared_result must be a "
                "PaymentOrchestrationResult."
            )
        )

    if (
        prepared_result.status
        != PaymentWorkflowStatus.PREPARED
    ):
        raise ValueError(
            (
                "Payment execution requires a "
                "PREPARED orchestration result."
            )
        )

    execution_result = (
        execute_payment_transaction(
            transaction=(
                prepared_result.transaction
            ),
            processed_at=processed_at,
        )
    )

    execution_event = (
        publish_payment_execution_recorded_event(
            transaction=(
                prepared_result.transaction
            ),
            execution_result=execution_result,
        )
    )

    if execution_result.status == "failed":
        workflow_status = (
            PaymentWorkflowStatus.EXECUTION_FAILED
        )

    else:
        workflow_status = (
            PaymentWorkflowStatus.EXECUTION_PENDING
        )

    return PaymentOrchestrationResult(
        obligation=prepared_result.obligation,
        payment_request=(
            prepared_result.payment_request
        ),
        intent=prepared_result.intent,
        transaction=prepared_result.transaction,
        status=workflow_status,
        execution_result=execution_result,
        published_events=(
            prepared_result.published_events
            + (
                execution_event,
            )
        ),
    )

def verify_and_reconcile_payment(
    *,
    executed_result: PaymentOrchestrationResult,
    evidence: ProviderVerificationEvidence,
    verified_at: datetime,
    reconciled_at: datetime,
) -> PaymentOrchestrationResult:
    """
    Continue one executed Payment Platform workflow using
    genuine provider-verification evidence.

    Processing order:

    1. Require an EXECUTION_PENDING workflow.
    2. Verify provider evidence against the authoritative
       PaymentTransaction.
    3. Persist the verification decision.
    4. Publish the verification event.
    5. Reconcile the verified decision.
    6. Persist the reconciliation decision.
    7. Publish the reconciliation event.
    8. Return a new immutable orchestration result.

    This function never manufactures provider evidence.
    """

    if not isinstance(
        executed_result,
        PaymentOrchestrationResult,
    ):
        raise ValueError(
            (
                "executed_result must be a "
                "PaymentOrchestrationResult."
            )
        )

    if (
        executed_result.status
        != PaymentWorkflowStatus.EXECUTION_PENDING
    ):
        raise ValueError(
            (
                "Payment verification requires an "
                "EXECUTION_PENDING orchestration result."
            )
        )

    if not isinstance(
        evidence,
        ProviderVerificationEvidence,
    ):
        raise ValueError(
            (
                "evidence must be "
                "ProviderVerificationEvidence."
            )
        )

    # ==========================================
    # VERIFICATION
    # ==========================================

    verification = verify_payment_evidence(
        transaction=(
            executed_result.transaction
        ),
        evidence=evidence,
        verified_at=verified_at,
    )

    persisted_verification = (
        save_payment_verification(
            verification
        )
    )

    verification_event = (
        publish_payment_verified_event(
            persisted_verification
        )
    )

    # ==========================================
    # RECONCILIATION
    # ==========================================

    reconciliation = reconcile_payment(
        transaction=(
            executed_result.transaction
        ),
        verification=(
            persisted_verification
        ),
        reconciled_at=reconciled_at,
    )

    persisted_reconciliation = (
        save_payment_reconciliation(
            reconciliation
        )
    )

    reconciliation_event = (
        publish_payment_reconciled_event(
            persisted_reconciliation
        )
    )

    # ==========================================
    # WORKFLOW OUTCOME
    # ==========================================

    if (
        persisted_verification.status
        == PaymentVerificationStatus.MATCHED
        and persisted_reconciliation.status
        == "reconciled"
    ):
        workflow_status = (
            PaymentWorkflowStatus.RECONCILED
        )

    elif (
        persisted_verification.status
        == PaymentVerificationStatus.PENDING
    ):
        workflow_status = (
            PaymentWorkflowStatus.VERIFICATION_PENDING
        )

    else:
        workflow_status = (
            PaymentWorkflowStatus.VERIFICATION_FAILED
        )

    return PaymentOrchestrationResult(
        obligation=executed_result.obligation,
        payment_request=(
            executed_result.payment_request
        ),
        intent=executed_result.intent,
        transaction=executed_result.transaction,
        status=workflow_status,
        execution_result=(
            executed_result.execution_result
        ),
        verification_result=(
            persisted_verification
        ),
        reconciliation_result=(
            persisted_reconciliation
        ),
        published_events=(
            executed_result.published_events
            + (
                verification_event,
                reconciliation_event,
            )
        ),
    )