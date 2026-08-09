"""
HABESHAGO Payment Repository

Provides durable persistence for canonical Payment Platform
domain objects.

Commit #95 establishes:
- exact Decimal storage
- timezone-preserving datetime storage
- authoritative reference-based lookup
- idempotent persistence
- conflicting replacement protection

Later sections of this repository persist:
PaymentRequest, PaymentIntent and PaymentTransaction.

This repository does not:
- contact payment providers
- process payments
- confirm provider success
- publish events
- perform reconciliation
"""

from datetime import (
    datetime,
)

from decimal import (
    Decimal,
)

from app.database.database import (
    create_connection,
)

from app.payments.exceptions import (
    PaymentPersistenceError,
)

from app.payments.models import (
    PaymentIntent,
    PaymentObligation,
    PaymentRequest,
    PaymentTransaction,
)


def _decimal_to_storage(
    value: Decimal,
) -> str:
    """
    Convert one authoritative Decimal to exact SQLite text.
    """

    if not isinstance(
        value,
        Decimal,
    ):
        raise PaymentPersistenceError(
            (
                "Payment money must be Decimal."
            )
        )

    if not value.is_finite():
        raise PaymentPersistenceError(
            (
                "Payment Decimal must be finite."
            )
        )

    return str(
        value
    )


def _storage_to_decimal(
    value,
) -> Decimal:
    """
    Reconstruct one authoritative Decimal from SQLite text.
    """

    if value is None:
        raise PaymentPersistenceError(
            (
                "Stored payment Decimal "
                "cannot be null."
            )
        )

    try:
        return Decimal(
            str(
                value
            )
        )

    except Exception as exc:
        raise PaymentPersistenceError(
            (
                "Stored payment Decimal "
                "is invalid."
            )
        ) from exc


def _datetime_to_storage(
    value: datetime,
) -> str:
    """
    Store a timezone-aware datetime as ISO-8601 text.
    """

    if not isinstance(
        value,
        datetime,
    ):
        raise PaymentPersistenceError(
            (
                "Payment datetime must be datetime."
            )
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PaymentPersistenceError(
            (
                "Payment datetime must be "
                "timezone-aware."
            )
        )

    return value.isoformat()


def _storage_to_datetime(
    value,
) -> datetime:
    """
    Restore one timezone-aware datetime from ISO-8601 text.
    """

    if value is None:
        raise PaymentPersistenceError(
            (
                "Stored payment datetime "
                "cannot be null."
            )
        )

    try:
        restored = datetime.fromisoformat(
            str(
                value
            )
        )

    except Exception as exc:
        raise PaymentPersistenceError(
            (
                "Stored payment datetime "
                "is invalid."
            )
        ) from exc

    if (
        restored.tzinfo is None
        or restored.utcoffset() is None
    ):
        raise PaymentPersistenceError(
            (
                "Stored payment datetime must be "
                "timezone-aware."
            )
        )

    return restored


def _row_to_obligation(
    row,
) -> PaymentObligation | None:
    """
    Convert one payment_obligations row into the canonical
    PaymentObligation domain model.
    """

    if row is None:
        return None

    return PaymentObligation(
        obligation_reference=str(
            row[0]
        ),
        source_type=str(
            row[1]
        ),
        source_reference=str(
            row[2]
        ),
        amount=_storage_to_decimal(
            row[3]
        ),
        currency=str(
            row[4]
        ),
        pricing_quote_id=(
            str(
                row[5]
            )
            if row[5] is not None
            else None
        ),
        pricing_request_id=(
            str(
                row[6]
            )
            if row[6] is not None
            else None
        ),
        created_at=_storage_to_datetime(
            row[7]
        ),
        contract_version=str(
            row[8]
        ),
    )


def get_payment_obligation(
    obligation_reference: str,
) -> PaymentObligation | None:
    """
    Return one canonical PaymentObligation by reference.

    Return None when no obligation exists.
    """

    normalized_reference = str(
        obligation_reference or ""
    ).strip()

    if not normalized_reference:
        raise PaymentPersistenceError(
            (
                "obligation_reference "
                "cannot be empty."
            )
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                obligation_reference,
                source_type,
                source_reference,
                amount,
                currency,
                pricing_quote_id,
                pricing_request_id,
                created_at,
                contract_version
            FROM payment_obligations
            WHERE obligation_reference = ?
            """,
            (
                normalized_reference,
            ),
        )

        return _row_to_obligation(
            cursor.fetchone()
        )

    finally:
        connection.close()


def save_payment_obligation(
    obligation: PaymentObligation,
) -> PaymentObligation:
    """
    Persist one authoritative PaymentObligation.

    Persistence is idempotent.

    Repeating the exact same obligation returns the existing
    canonical obligation.

    Reusing the same obligation_reference for different
    money, provenance or contract data is blocked.
    """

    if not isinstance(
        obligation,
        PaymentObligation,
    ):
        raise PaymentPersistenceError(
            (
                "obligation must be a "
                "PaymentObligation."
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
                obligation_reference,
                source_type,
                source_reference,
                amount,
                currency,
                pricing_quote_id,
                pricing_request_id,
                created_at,
                contract_version
            FROM payment_obligations
            WHERE obligation_reference = ?
            """,
            (
                obligation.obligation_reference,
            ),
        )

        existing = _row_to_obligation(
            cursor.fetchone()
        )

        if existing is not None:
            if existing == obligation:
                return existing

            raise PaymentPersistenceError(
                (
                    "Payment obligation reference "
                    "already belongs to a different "
                    "authoritative obligation."
                )
            )

        cursor.execute(
            """
            INSERT INTO payment_obligations (
                obligation_reference,
                source_type,
                source_reference,
                amount,
                currency,
                pricing_quote_id,
                pricing_request_id,
                created_at,
                contract_version
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                obligation.obligation_reference,
                obligation.source_type,
                obligation.source_reference,
                _decimal_to_storage(
                    obligation.amount
                ),
                obligation.currency,
                obligation.pricing_quote_id,
                obligation.pricing_request_id,
                _datetime_to_storage(
                    obligation.created_at
                ),
                obligation.contract_version,
            ),
        )

        connection.commit()

        return obligation

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def _row_to_request(
    row,
    *,
    obligation: PaymentObligation,
) -> PaymentRequest | None:
    """
    Convert one payment_requests row into the canonical
    PaymentRequest domain model.
    """

    if row is None:
        return None

    return PaymentRequest(
        obligation=obligation,
        payer_id=int(
            row[1]
        ),
        payment_method=str(
            row[2]
        ),
        request_reference=str(
            row[0]
        ),
        status=str(
            row[3]
        ),
        requested_at=_storage_to_datetime(
            row[4]
        ),
        contract_version=str(
            row[5]
        ),
    )


def get_payment_request(
    request_reference: str,
) -> PaymentRequest | None:
    """
    Return one canonical PaymentRequest by reference.

    The linked canonical PaymentObligation is restored as
    part of the domain object.
    """

    normalized_reference = str(
        request_reference or ""
    ).strip()

    if not normalized_reference:
        raise PaymentPersistenceError(
            (
                "request_reference "
                "cannot be empty."
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
                request_reference,
                obligation_reference,
                payer_id,
                payment_method,
                status,
                requested_at,
                contract_version
            FROM payment_requests
            WHERE request_reference = ?
            """,
            (
                normalized_reference,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        obligation_reference = str(
            row[1]
        )

        cursor.execute(
            """
            SELECT
                obligation_reference,
                source_type,
                source_reference,
                amount,
                currency,
                pricing_quote_id,
                pricing_request_id,
                created_at,
                contract_version
            FROM payment_obligations
            WHERE obligation_reference = ?
            """,
            (
                obligation_reference,
            ),
        )

        obligation = _row_to_obligation(
            cursor.fetchone()
        )

        if obligation is None:
            raise PaymentPersistenceError(
                (
                    "PaymentRequest references a "
                    "missing PaymentObligation."
                )
            )

        request_row = (
            row[0],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
        )

        return _row_to_request(
            request_row,
            obligation=obligation,
        )

    finally:
        connection.close()


def save_payment_request(
    request: PaymentRequest,
) -> PaymentRequest:
    """
    Persist one authoritative PaymentRequest.

    The linked PaymentObligation must already exist and
    must exactly equal the request's obligation.

    Persistence is idempotent.

    Reusing a request_reference for different payment
    facts is blocked.
    """

    if not isinstance(
        request,
        PaymentRequest,
    ):
        raise PaymentPersistenceError(
            (
                "request must be a "
                "PaymentRequest."
            )
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        # ======================================
        # VERIFY AUTHORITATIVE OBLIGATION
        # ======================================

        cursor.execute(
            """
            SELECT
                obligation_reference,
                source_type,
                source_reference,
                amount,
                currency,
                pricing_quote_id,
                pricing_request_id,
                created_at,
                contract_version
            FROM payment_obligations
            WHERE obligation_reference = ?
            """,
            (
                request
                .obligation
                .obligation_reference,
            ),
        )

        stored_obligation = (
            _row_to_obligation(
                cursor.fetchone()
            )
        )

        if stored_obligation is None:
            raise PaymentPersistenceError(
                (
                    "PaymentRequest requires its "
                    "PaymentObligation to be persisted "
                    "first."
                )
            )

        if (
            stored_obligation
            != request.obligation
        ):
            raise PaymentPersistenceError(
                (
                    "Stored PaymentObligation does not "
                    "match the PaymentRequest "
                    "obligation."
                )
            )

        # ======================================
        # IDEMPOTENCY CHECK
        # ======================================

        cursor.execute(
            """
            SELECT
                request_reference,
                payer_id,
                payment_method,
                status,
                requested_at,
                contract_version
            FROM payment_requests
            WHERE request_reference = ?
            """,
            (
                request.request_reference,
            ),
        )

        existing = _row_to_request(
            cursor.fetchone(),
            obligation=stored_obligation,
        )

        if existing is not None:
            if existing == request:
                return existing

            raise PaymentPersistenceError(
                (
                    "Payment request reference "
                    "already belongs to a different "
                    "authoritative request."
                )
            )

        # ======================================
        # INSERT
        # ======================================

        cursor.execute(
            """
            INSERT INTO payment_requests (
                request_reference,
                obligation_reference,
                payer_id,
                payment_method,
                status,
                requested_at,
                contract_version
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                request.request_reference,
                (
                    request
                    .obligation
                    .obligation_reference
                ),
                request.payer_id,
                request.payment_method,
                request.status,
                _datetime_to_storage(
                    request.requested_at
                ),
                request.contract_version,
            ),
        )

        connection.commit()

        return request

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def _load_obligation_with_cursor(
    cursor,
    obligation_reference: str,
) -> PaymentObligation | None:
    """
    Load one PaymentObligation using an existing cursor.
    """

    cursor.execute(
        """
        SELECT
            obligation_reference,
            source_type,
            source_reference,
            amount,
            currency,
            pricing_quote_id,
            pricing_request_id,
            created_at,
            contract_version
        FROM payment_obligations
        WHERE obligation_reference = ?
        """,
        (
            obligation_reference,
        ),
    )

    return _row_to_obligation(
        cursor.fetchone()
    )


def _load_request_with_cursor(
    cursor,
    request_reference: str,
) -> PaymentRequest | None:
    """
    Load one PaymentRequest and its authoritative
    PaymentObligation using an existing cursor.
    """

    cursor.execute(
        """
        SELECT
            request_reference,
            obligation_reference,
            payer_id,
            payment_method,
            status,
            requested_at,
            contract_version
        FROM payment_requests
        WHERE request_reference = ?
        """,
        (
            request_reference,
        ),
    )

    row = cursor.fetchone()

    if row is None:
        return None

    obligation = (
        _load_obligation_with_cursor(
            cursor,
            str(
                row[1]
            ),
        )
    )

    if obligation is None:
        raise PaymentPersistenceError(
            (
                "Stored PaymentRequest references "
                "a missing PaymentObligation."
            )
        )

    request_row = (
        row[0],
        row[2],
        row[3],
        row[4],
        row[5],
        row[6],
    )

    return _row_to_request(
        request_row,
        obligation=obligation,
    )


def _row_to_intent(
    row,
    *,
    payment_request: PaymentRequest,
) -> PaymentIntent | None:
    """
    Convert one payment_intents row into the canonical
    PaymentIntent domain model.
    """

    if row is None:
        return None

    return PaymentIntent(
        payment_request=payment_request,
        provider=str(
            row[1]
        ),
        intent_reference=str(
            row[0]
        ),
        status=str(
            row[2]
        ),
        created_at=_storage_to_datetime(
            row[3]
        ),
        expires_at=(
            _storage_to_datetime(
                row[4]
            )
            if row[4] is not None
            else None
        ),
        contract_version=str(
            row[5]
        ),
    )


def get_payment_intent(
    intent_reference: str,
) -> PaymentIntent | None:
    """
    Return one canonical PaymentIntent by reference.

    The complete PaymentRequest and PaymentObligation chain
    is reconstructed.
    """

    normalized_reference = str(
        intent_reference or ""
    ).strip()

    if not normalized_reference:
        raise PaymentPersistenceError(
            (
                "intent_reference "
                "cannot be empty."
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
                intent_reference,
                request_reference,
                provider,
                status,
                created_at,
                expires_at,
                contract_version
            FROM payment_intents
            WHERE intent_reference = ?
            """,
            (
                normalized_reference,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        payment_request = (
            _load_request_with_cursor(
                cursor,
                str(
                    row[1]
                ),
            )
        )

        if payment_request is None:
            raise PaymentPersistenceError(
                (
                    "PaymentIntent references a "
                    "missing PaymentRequest."
                )
            )

        intent_row = (
            row[0],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
        )

        return _row_to_intent(
            intent_row,
            payment_request=payment_request,
        )

    finally:
        connection.close()


def save_payment_intent(
    intent: PaymentIntent,
) -> PaymentIntent:
    """
    Persist one authoritative PaymentIntent.

    The complete linked PaymentRequest must already be
    persisted and must exactly match the intent's request.

    Persistence is idempotent.

    Reusing an intent_reference for different payment facts
    is blocked.
    """

    if not isinstance(
        intent,
        PaymentIntent,
    ):
        raise PaymentPersistenceError(
            (
                "intent must be a "
                "PaymentIntent."
            )
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        # ======================================
        # VERIFY AUTHORITATIVE REQUEST
        # ======================================

        stored_request = (
            _load_request_with_cursor(
                cursor,
                (
                    intent
                    .payment_request
                    .request_reference
                ),
            )
        )

        if stored_request is None:
            raise PaymentPersistenceError(
                (
                    "PaymentIntent requires its "
                    "PaymentRequest to be persisted "
                    "first."
                )
            )

        if (
            stored_request
            != intent.payment_request
        ):
            raise PaymentPersistenceError(
                (
                    "Stored PaymentRequest does not "
                    "match the PaymentIntent request."
                )
            )

        # ======================================
        # IDEMPOTENCY CHECK
        # ======================================

        cursor.execute(
            """
            SELECT
                intent_reference,
                provider,
                status,
                created_at,
                expires_at,
                contract_version
            FROM payment_intents
            WHERE intent_reference = ?
            """,
            (
                intent.intent_reference,
            ),
        )

        existing = _row_to_intent(
            cursor.fetchone(),
            payment_request=stored_request,
        )

        if existing is not None:
            if existing == intent:
                return existing

            raise PaymentPersistenceError(
                (
                    "Payment intent reference "
                    "already belongs to a different "
                    "authoritative intent."
                )
            )

        # ======================================
        # INSERT
        # ======================================

        cursor.execute(
            """
            INSERT INTO payment_intents (
                intent_reference,
                request_reference,
                provider,
                status,
                created_at,
                expires_at,
                contract_version
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                intent.intent_reference,
                (
                    intent
                    .payment_request
                    .request_reference
                ),
                intent.provider,
                intent.status,
                _datetime_to_storage(
                    intent.created_at
                ),
                (
                    _datetime_to_storage(
                        intent.expires_at
                    )
                    if intent.expires_at
                    is not None
                    else None
                ),
                intent.contract_version,
            ),
        )

        connection.commit()

        return intent

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def _load_intent_with_cursor(
    cursor,
    intent_reference: str,
) -> PaymentIntent | None:
    """
    Load one PaymentIntent and its complete authoritative
    PaymentRequest / PaymentObligation chain.
    """

    cursor.execute(
        """
        SELECT
            intent_reference,
            request_reference,
            provider,
            status,
            created_at,
            expires_at,
            contract_version
        FROM payment_intents
        WHERE intent_reference = ?
        """,
        (
            intent_reference,
        ),
    )

    row = cursor.fetchone()

    if row is None:
        return None

    payment_request = (
        _load_request_with_cursor(
            cursor,
            str(
                row[1]
            ),
        )
    )

    if payment_request is None:
        raise PaymentPersistenceError(
            (
                "Stored PaymentIntent references "
                "a missing PaymentRequest."
            )
        )

    intent_row = (
        row[0],
        row[2],
        row[3],
        row[4],
        row[5],
        row[6],
    )

    return _row_to_intent(
        intent_row,
        payment_request=payment_request,
    )


def _row_to_transaction(
    row,
) -> PaymentTransaction | None:
    """
    Convert one payment_transactions row into the canonical
    PaymentTransaction domain model.
    """

    if row is None:
        return None

    return PaymentTransaction(
        transaction_reference=str(
            row[0]
        ),
        intent_reference=str(
            row[1]
        ),
        provider=str(
            row[2]
        ),
        payment_method=str(
            row[3]
        ),
        amount=_storage_to_decimal(
            row[4]
        ),
        currency=str(
            row[5]
        ),
        status=str(
            row[6]
        ),
        payer_id=int(
            row[7]
        ),
        obligation_reference=str(
            row[8]
        ),
        created_at=_storage_to_datetime(
            row[9]
        ),
        provider_reference=(
            str(
                row[10]
            )
            if row[10] is not None
            else None
        ),
        failure_reason=(
            str(
                row[11]
            )
            if row[11] is not None
            else None
        ),
        contract_version=str(
            row[12]
        ),
    )


def get_payment_transaction(
    transaction_reference: str,
) -> PaymentTransaction | None:
    """
    Return one canonical PaymentTransaction by reference.
    """

    normalized_reference = str(
        transaction_reference or ""
    ).strip()

    if not normalized_reference:
        raise PaymentPersistenceError(
            (
                "transaction_reference "
                "cannot be empty."
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
                transaction_reference,
                intent_reference,
                provider,
                payment_method,
                amount,
                currency,
                status,
                payer_id,
                obligation_reference,
                created_at,
                provider_reference,
                failure_reason,
                contract_version
            FROM payment_transactions
            WHERE transaction_reference = ?
            """,
            (
                normalized_reference,
            ),
        )

        return _row_to_transaction(
            cursor.fetchone()
        )

    finally:
        connection.close()


def save_payment_transaction(
    transaction: PaymentTransaction,
) -> PaymentTransaction:
    """
    Persist one authoritative PaymentTransaction.

    The linked PaymentIntent and PaymentObligation must
    already exist and must agree with the transaction.

    Persistence is idempotent.

    Reusing a transaction_reference for different payment
    facts is blocked.
    """

    if not isinstance(
        transaction,
        PaymentTransaction,
    ):
        raise PaymentPersistenceError(
            (
                "transaction must be a "
                "PaymentTransaction."
            )
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys = ON"
        )

        # ======================================
        # VERIFY AUTHORITATIVE INTENT
        # ======================================

        stored_intent = (
            _load_intent_with_cursor(
                cursor,
                transaction.intent_reference,
            )
        )

        if stored_intent is None:
            raise PaymentPersistenceError(
                (
                    "PaymentTransaction requires its "
                    "PaymentIntent to be persisted first."
                )
            )

        authoritative_request = (
            stored_intent.payment_request
        )

        authoritative_obligation = (
            authoritative_request.obligation
        )

        if (
            transaction.provider
            != stored_intent.provider
        ):
            raise PaymentPersistenceError(
                (
                    "PaymentTransaction provider does "
                    "not match the authoritative "
                    "PaymentIntent provider."
                )
            )

        if (
            transaction.payment_method
            != authoritative_request.payment_method
        ):
            raise PaymentPersistenceError(
                (
                    "PaymentTransaction payment_method "
                    "does not match the authoritative "
                    "PaymentRequest."
                )
            )

        if (
            transaction.payer_id
            != authoritative_request.payer_id
        ):
            raise PaymentPersistenceError(
                (
                    "PaymentTransaction payer_id does "
                    "not match the authoritative "
                    "PaymentRequest."
                )
            )

        if (
            transaction.obligation_reference
            != authoritative_obligation.obligation_reference
        ):
            raise PaymentPersistenceError(
                (
                    "PaymentTransaction obligation "
                    "reference does not match the "
                    "authoritative PaymentObligation."
                )
            )

        if (
            transaction.amount
            != authoritative_obligation.amount
        ):
            raise PaymentPersistenceError(
                (
                    "PaymentTransaction amount does "
                    "not match the authoritative "
                    "PaymentObligation amount."
                )
            )

        if (
            transaction.currency
            != authoritative_obligation.currency
        ):
            raise PaymentPersistenceError(
                (
                    "PaymentTransaction currency does "
                    "not match the authoritative "
                    "PaymentObligation currency."
                )
            )

        # ======================================
        # IDEMPOTENCY CHECK
        # ======================================

        cursor.execute(
            """
            SELECT
                transaction_reference,
                intent_reference,
                provider,
                payment_method,
                amount,
                currency,
                status,
                payer_id,
                obligation_reference,
                created_at,
                provider_reference,
                failure_reason,
                contract_version
            FROM payment_transactions
            WHERE transaction_reference = ?
            """,
            (
                transaction.transaction_reference,
            ),
        )

        existing = _row_to_transaction(
            cursor.fetchone()
        )

        if existing is not None:
            if existing == transaction:
                return existing

            raise PaymentPersistenceError(
                (
                    "Payment transaction reference "
                    "already belongs to a different "
                    "authoritative transaction."
                )
            )

        # ======================================
        # INSERT
        # ======================================

        cursor.execute(
            """
            INSERT INTO payment_transactions (
                transaction_reference,
                intent_reference,
                provider,
                payment_method,
                amount,
                currency,
                status,
                payer_id,
                obligation_reference,
                created_at,
                provider_reference,
                failure_reason,
                contract_version
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                transaction.transaction_reference,
                transaction.intent_reference,
                transaction.provider,
                transaction.payment_method,
                _decimal_to_storage(
                    transaction.amount
                ),
                transaction.currency,
                transaction.status,
                transaction.payer_id,
                transaction.obligation_reference,
                _datetime_to_storage(
                    transaction.created_at
                ),
                transaction.provider_reference,
                transaction.failure_reason,
                transaction.contract_version,
            ),
        )

        connection.commit()

        return transaction

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()