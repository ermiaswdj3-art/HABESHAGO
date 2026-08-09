"""
HABESHAGO Payment Verification and Reconciliation
Repository

Persists authoritative payment verification and
reconciliation decisions.

Commit #97 guarantees:
- reference-based authority
- timezone-preserving timestamps
- deterministic field provenance
- idempotent retries
- conflicting historical rewrites are blocked
"""

from app.database.database import (
    create_connection,
)

from app.payments.exceptions import (
    PaymentPersistenceError,
)

from app.payments.reconciliation import (
    PaymentReconciliationResult,
)

from app.payments.verification import (
    PaymentVerificationResult,
)


_FIELD_SEPARATOR = "|"


def _fields_to_storage(
    values: tuple[str, ...],
) -> str:
    """
    Persist deterministic tuple field provenance.
    """

    if not isinstance(
        values,
        tuple,
    ):
        raise PaymentPersistenceError(
            "Verification fields must be tuple."
        )

    return _FIELD_SEPARATOR.join(
        values
    )


def _storage_to_fields(
    value,
) -> tuple[str, ...]:
    """
    Restore deterministic tuple field provenance.
    """

    text = str(
        value or ""
    )

    if not text:
        return ()

    return tuple(
        text.split(
            _FIELD_SEPARATOR
        )
    )


def _datetime_to_storage(
    value,
) -> str:
    """
    Persist one timezone-aware datetime.
    """

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PaymentPersistenceError(
            (
                "Payment reconciliation datetime "
                "must be timezone-aware."
            )
        )

    return value.isoformat()


def save_payment_verification(
    verification: PaymentVerificationResult,
) -> PaymentVerificationResult:
    """
    Persist one authoritative verification result.

    An identical retry is idempotent.

    A different result for the same transaction reference
    is blocked.
    """

    if not isinstance(
        verification,
        PaymentVerificationResult,
    ):
        raise PaymentPersistenceError(
            (
                "verification must be a "
                "PaymentVerificationResult."
            )
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor.execute(
            """
            SELECT
                provider,
                provider_reference,
                status,
                verified_at,
                matched_fields,
                mismatched_fields,
                reason
            FROM payment_verifications
            WHERE transaction_reference = ?
            """,
            (
                verification.transaction_reference,
            ),
        )

        row = cursor.fetchone()

        stored = (
            None
            if row is None
            else (
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
            )
        )

        incoming = (
            verification.provider,
            verification.provider_reference,
            verification.status,
            _datetime_to_storage(
                verification.verified_at
            ),
            _fields_to_storage(
                verification.matched_fields
            ),
            _fields_to_storage(
                verification.mismatched_fields
            ),
            verification.reason,
        )

        if stored is not None:
            if stored == incoming:
                return verification

            raise PaymentPersistenceError(
                (
                    "Payment transaction already has "
                    "a different authoritative "
                    "verification result."
                )
            )

        cursor.execute(
            """
            INSERT INTO payment_verifications (
                transaction_reference,
                provider,
                provider_reference,
                status,
                verified_at,
                matched_fields,
                mismatched_fields,
                reason
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                verification.transaction_reference,
                *incoming,
            ),
        )

        connection.commit()

        return verification

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_payment_reconciliation(
    reconciliation: PaymentReconciliationResult,
) -> PaymentReconciliationResult:
    """
    Persist one authoritative reconciliation result.

    An identical retry is idempotent.

    A conflicting historical rewrite is blocked.
    """

    if not isinstance(
        reconciliation,
        PaymentReconciliationResult,
    ):
        raise PaymentPersistenceError(
            (
                "reconciliation must be a "
                "PaymentReconciliationResult."
            )
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        cursor.execute(
            """
            SELECT
                provider,
                provider_reference,
                status,
                reconciled_at,
                reason
            FROM payment_reconciliations
            WHERE transaction_reference = ?
            """,
            (
                reconciliation.transaction_reference,
            ),
        )

        row = cursor.fetchone()

        incoming = (
            reconciliation.provider,
            reconciliation.provider_reference,
            reconciliation.status,
            _datetime_to_storage(
                reconciliation.reconciled_at
            ),
            reconciliation.reason,
        )

        if row is not None:
            stored = tuple(
                row
            )

            if stored == incoming:
                return reconciliation

            raise PaymentPersistenceError(
                (
                    "Payment transaction already has "
                    "a different authoritative "
                    "reconciliation result."
                )
            )

        cursor.execute(
            """
            INSERT INTO payment_reconciliations (
                transaction_reference,
                provider,
                provider_reference,
                status,
                reconciled_at,
                reason
            )
            VALUES (
                ?, ?, ?, ?, ?, ?
            )
            """,
            (
                reconciliation.transaction_reference,
                *incoming,
            ),
        )

        connection.commit()

        return reconciliation

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()