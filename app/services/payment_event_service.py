"""
HABESHAGO Payment Event Service

Converts authoritative Payment Platform decisions into
canonical HABESHAGO platform events.

Responsibilities:
- Build Payment Transaction events
- Build Payment Execution events
- Build Payment Verification events
- Build Payment Reconciliation events
- Publish through the shared Event Engine
- Preserve deterministic logical event identity

This service observes authoritative Payment Platform
results.

It does not:
- create payment obligations
- execute provider requests
- verify provider evidence
- reconcile payments
- mutate payment state
- persist payment records
"""

import uuid

from app.constants.event_types import (
    EventType,
)

from app.models.event import (
    Event,
)

from app.payments.models import (
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

from app.services.event_engine import (
    publish_event,
)


def _build_payment_event_id(
    *,
    event_type: str,
    source: str,
    transaction_reference: str,
) -> str:
    """
    Build a deterministic identity for one logical Payment
    Platform event.

    Retrying publication of the same authoritative payment
    fact therefore produces the same event_id.

    Including source prevents distinct payment stages that
    share an event type such as PAYMENT_FAILED from
    colliding.
    """

    normalized_event_type = str(
        event_type or ""
    ).strip()

    normalized_source = str(
        source or ""
    ).strip()

    normalized_transaction_reference = str(
        transaction_reference or ""
    ).strip()

    if not normalized_event_type:
        raise ValueError(
            "event_type cannot be empty."
        )

    if not normalized_source:
        raise ValueError(
            "source cannot be empty."
        )

    if not normalized_transaction_reference:
        raise ValueError(
            (
                "transaction_reference cannot "
                "be empty."
            )
        )

    logical_identity = (
        "habeshago:payment:"
        f"{normalized_source}:"
        f"{normalized_event_type}:"
        f"{normalized_transaction_reference}"
    )

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            logical_identity,
        )
    )


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
        raise ValueError(
            f"{field_name} must be str."
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return normalized


def build_payment_transaction_created_event(
    transaction: PaymentTransaction,
) -> Event:
    """
    Build one canonical event for a newly created
    authoritative PaymentTransaction.
    """

    if not isinstance(
        transaction,
        PaymentTransaction,
    ):
        raise ValueError(
            (
                "transaction must be a "
                "PaymentTransaction."
            )
        )

    event_type = (
        EventType.PAYMENT_TRANSACTION_CREATED
    )

    source = "PaymentPlatform"

    return Event(
        event_id=_build_payment_event_id(
            event_type=event_type,
            source=source,
            transaction_reference=(
                transaction.transaction_reference
            ),
        ),
        event_type=event_type,
        entity="payment_transaction",
        source=source,
        payload={
            "entity_id": (
                transaction.transaction_reference
            ),
            "transaction_reference": (
                transaction.transaction_reference
            ),
            "intent_reference": (
                transaction.intent_reference
            ),
            "obligation_reference": (
                transaction.obligation_reference
            ),
            "provider": transaction.provider,
            "payment_method": (
                transaction.payment_method
            ),
            "currency": transaction.currency,
            "amount": str(
                transaction.amount
            ),
            "status": transaction.status,
            "payer_id": transaction.payer_id,
            "created_at": (
                transaction.created_at.isoformat()
            ),
        },
    )


def build_payment_execution_recorded_event(
    *,
    transaction: PaymentTransaction,
    execution_result: PaymentExecutionResult,
) -> Event:
    """
    Build one canonical event from one provider execution
    result.
    """

    if not isinstance(
        transaction,
        PaymentTransaction,
    ):
        raise ValueError(
            (
                "transaction must be a "
                "PaymentTransaction."
            )
        )

    if not isinstance(
        execution_result,
        PaymentExecutionResult,
    ):
        raise ValueError(
            (
                "execution_result must be a "
                "PaymentExecutionResult."
            )
        )

    if (
        execution_result.transaction_reference
        != transaction.transaction_reference
    ):
        raise ValueError(
            (
                "Execution result transaction "
                "reference does not match the "
                "PaymentTransaction."
            )
        )

    if (
        execution_result.provider
        != transaction.provider
    ):
        raise ValueError(
            (
                "Execution result provider does "
                "not match the PaymentTransaction."
            )
        )

    event_type = (
        EventType.PAYMENT_FAILED
        if execution_result.status == "failed"
        else EventType.PAYMENT_EXECUTION_RECORDED
    )

    source = "PaymentExecutionPlatform"

    return Event(
        event_id=_build_payment_event_id(
            event_type=event_type,
            source=source,
            transaction_reference=(
                transaction.transaction_reference
            ),
        ),
        event_type=event_type,
        entity="payment_transaction",
        source=source,
        payload={
            "entity_id": (
                transaction.transaction_reference
            ),
            "transaction_reference": (
                transaction.transaction_reference
            ),
            "obligation_reference": (
                transaction.obligation_reference
            ),
            "provider": transaction.provider,
            "payment_method": (
                transaction.payment_method
            ),
            "currency": transaction.currency,
            "amount": str(
                transaction.amount
            ),
            "execution_status": (
                execution_result.status
            ),
            "provider_reference": (
                execution_result.provider_reference
            ),
            "failure_reason": (
                execution_result.failure_reason
            ),
            "processed_at": (
                execution_result
                .processed_at
                .isoformat()
            ),
        },
    )


def build_payment_verified_event(
    verification: PaymentVerificationResult,
) -> Event:
    """
    Build one canonical Payment Verification event.
    """

    if not isinstance(
        verification,
        PaymentVerificationResult,
    ):
        raise ValueError(
            (
                "verification must be a "
                "PaymentVerificationResult."
            )
        )

    event_type = (
        EventType.PAYMENT_FAILED
        if verification.status
        in {
            "failed",
            "mismatched",
        }
        else EventType.PAYMENT_VERIFIED
    )

    source = "PaymentVerificationPlatform"

    return Event(
        event_id=_build_payment_event_id(
            event_type=event_type,
            source=source,
            transaction_reference=(
                verification.transaction_reference
            ),
        ),
        event_type=event_type,
        entity="payment_verification",
        source=source,
        payload={
            "entity_id": (
                verification.transaction_reference
            ),
            "transaction_reference": (
                verification.transaction_reference
            ),
            "provider": verification.provider,
            "provider_reference": (
                verification.provider_reference
            ),
            "verification_status": (
                verification.status
            ),
            "matched_fields": (
                verification.matched_fields
            ),
            "mismatched_fields": (
                verification.mismatched_fields
            ),
            "reason": verification.reason,
            "verified_at": (
                verification
                .verified_at
                .isoformat()
            ),
        },
    )


def build_payment_reconciled_event(
    reconciliation: PaymentReconciliationResult,
) -> Event:
    """
    Build one canonical Payment Reconciliation event.
    """

    if not isinstance(
        reconciliation,
        PaymentReconciliationResult,
    ):
        raise ValueError(
            (
                "reconciliation must be a "
                "PaymentReconciliationResult."
            )
        )

    event_type = (
        EventType.PAYMENT_RECONCILED
        if reconciliation.status
        == "reconciled"
        else EventType.PAYMENT_FAILED
    )

    source = "PaymentReconciliationPlatform"

    return Event(
        event_id=_build_payment_event_id(
            event_type=event_type,
            source=source,
            transaction_reference=(
                reconciliation.transaction_reference
            ),
        ),
        event_type=event_type,
        entity="payment_reconciliation",
        source=source,
        payload={
            "entity_id": (
                reconciliation.transaction_reference
            ),
            "transaction_reference": (
                reconciliation.transaction_reference
            ),
            "provider": reconciliation.provider,
            "provider_reference": (
                reconciliation.provider_reference
            ),
            "reconciliation_status": (
                reconciliation.status
            ),
            "reason": reconciliation.reason,
            "reconciled_at": (
                reconciliation
                .reconciled_at
                .isoformat()
            ),
        },
    )


def publish_payment_transaction_created_event(
    transaction: PaymentTransaction,
) -> Event:
    """
    Build and publish one Payment Transaction event.
    """

    event = (
        build_payment_transaction_created_event(
            transaction
        )
    )

    publish_event(
        event
    )

    return event


def publish_payment_execution_recorded_event(
    *,
    transaction: PaymentTransaction,
    execution_result: PaymentExecutionResult,
) -> Event:
    """
    Build and publish one Payment Execution event.
    """

    event = (
        build_payment_execution_recorded_event(
            transaction=transaction,
            execution_result=execution_result,
        )
    )

    publish_event(
        event
    )

    return event


def publish_payment_verified_event(
    verification: PaymentVerificationResult,
) -> Event:
    """
    Build and publish one Payment Verification event.
    """

    event = build_payment_verified_event(
        verification
    )

    publish_event(
        event
    )

    return event


def publish_payment_reconciled_event(
    reconciliation: PaymentReconciliationResult,
) -> Event:
    """
    Build and publish one Payment Reconciliation event.
    """

    event = build_payment_reconciled_event(
        reconciliation
    )

    publish_event(
        event
    )

    return event