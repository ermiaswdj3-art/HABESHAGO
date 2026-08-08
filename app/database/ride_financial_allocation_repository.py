"""
HABESHAGO Ride Financial Allocation Repository

Provides persistent access to authoritative Decimal-native
financial allocations created by the Pricing Platform.

Financial Decimal values are persisted as exact SQLite TEXT
and reconstructed as Decimal values.

One ride may have only one authoritative financial
allocation.

Repeated persistence of the exact same allocation is
idempotent.

An attempt to replace an existing ride allocation with
different financial values or policy provenance is blocked.
"""

from decimal import (
    Decimal,
)

from app.database.database import (
    create_connection,
)

from app.pricing.financial import (
    FinancialAllocation,
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
        raise ValueError(
            (
                "Financial allocation money "
                "must be Decimal."
            )
        )

    if not value.is_finite():
        raise ValueError(
            (
                "Financial allocation Decimal "
                "must be finite."
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
        raise ValueError(
            (
                "Stored financial allocation "
                "Decimal cannot be null."
            )
        )

    return Decimal(
        str(
            value
        )
    )


def _row_to_allocation(
    row,
) -> FinancialAllocation | None:
    """
    Convert one database row into a FinancialAllocation.
    """

    if row is None:
        return None

    return FinancialAllocation(
        passenger_fare=(
            _storage_to_decimal(
                row[0]
            )
        ),
        commission_rate=(
            _storage_to_decimal(
                row[1]
            )
        ),
        commission_amount=(
            _storage_to_decimal(
                row[2]
            )
        ),
        driver_earnings=(
            _storage_to_decimal(
                row[3]
            )
        ),
        currency=str(
            row[4]
        ),
        commission_policy_version=str(
            row[5]
        ),
        commission_policy_reference=str(
            row[6]
        ),
    )


def get_ride_financial_allocation(
    ride_id: int,
) -> FinancialAllocation | None:
    """
    Return the authoritative financial allocation for one
    ride.

    Return None when the ride does not yet have an
    authoritative allocation.
    """

    if (
        not isinstance(
            ride_id,
            int,
        )
        or isinstance(
            ride_id,
            bool,
        )
        or ride_id <= 0
    ):
        raise ValueError(
            (
                "ride_id must be a positive "
                "integer."
            )
        )

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                passenger_fare,
                commission_rate,
                commission_amount,
                driver_earnings,
                currency,
                commission_policy_version,
                commission_policy_reference
            FROM ride_financial_allocations
            WHERE ride_id = ?
            """,
            (
                ride_id,
            ),
        )

        return _row_to_allocation(
            cursor.fetchone()
        )

    finally:
        connection.close()


def save_ride_financial_allocation(
    *,
    ride_id: int,
    allocation: FinancialAllocation,
) -> FinancialAllocation:
    """
    Persist one authoritative financial allocation.

    This operation is idempotent.

    If the ride already has the exact same allocation,
    return that stored allocation.

    If the ride already has a different allocation, block
    replacement so historical financial authority cannot
    silently change.
    """

    if (
        not isinstance(
            ride_id,
            int,
        )
        or isinstance(
            ride_id,
            bool,
        )
        or ride_id <= 0
    ):
        raise ValueError(
            (
                "ride_id must be a positive "
                "integer."
            )
        )

    if not isinstance(
        allocation,
        FinancialAllocation,
    ):
        raise ValueError(
            (
                "allocation must be a "
                "FinancialAllocation."
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
                passenger_fare,
                commission_rate,
                commission_amount,
                driver_earnings,
                currency,
                commission_policy_version,
                commission_policy_reference
            FROM ride_financial_allocations
            WHERE ride_id = ?
            """,
            (
                ride_id,
            ),
        )

        existing = _row_to_allocation(
            cursor.fetchone()
        )

        if existing is not None:
            if existing == allocation:
                return existing

            raise ValueError(
                (
                    "Ride already has a different "
                    "authoritative financial "
                    "allocation."
                )
            )

        cursor.execute(
            """
            INSERT INTO ride_financial_allocations (
                ride_id,
                passenger_fare,
                commission_rate,
                commission_amount,
                driver_earnings,
                currency,
                commission_policy_version,
                commission_policy_reference
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                ride_id,
                _decimal_to_storage(
                    allocation.passenger_fare
                ),
                _decimal_to_storage(
                    allocation.commission_rate
                ),
                _decimal_to_storage(
                    allocation.commission_amount
                ),
                _decimal_to_storage(
                    allocation.driver_earnings
                ),
                allocation.currency,
                (
                    allocation
                    .commission_policy_version
                ),
                (
                    allocation
                    .commission_policy_reference
                ),
            ),
        )

        connection.commit()

        return allocation

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def persist_ride_financial_allocation(
    *,
    cursor,
    ride_id: int,
    allocation: FinancialAllocation,
) -> FinancialAllocation:
    """
    Persist one authoritative financial allocation using
    an existing database transaction.

    This function allows Ride Settlement to persist the
    canonical Decimal allocation and lifecycle completion
    atomically.

    Repeating the exact allocation is idempotent.

    Replacing an existing allocation with different money
    or policy provenance is blocked.
    """

    if cursor is None:
        raise ValueError(
            "cursor is required."
        )

    if (
        not isinstance(
            ride_id,
            int,
        )
        or isinstance(
            ride_id,
            bool,
        )
        or ride_id <= 0
    ):
        raise ValueError(
            (
                "ride_id must be a positive "
                "integer."
            )
        )

    if not isinstance(
        allocation,
        FinancialAllocation,
    ):
        raise ValueError(
            (
                "allocation must be a "
                "FinancialAllocation."
            )
        )

    cursor.execute(
        """
        SELECT
            passenger_fare,
            commission_rate,
            commission_amount,
            driver_earnings,
            currency,
            commission_policy_version,
            commission_policy_reference
        FROM ride_financial_allocations
        WHERE ride_id = ?
        """,
        (
            ride_id,
        ),
    )

    existing = _row_to_allocation(
        cursor.fetchone()
    )

    if existing is not None:
        if existing == allocation:
            return existing

        raise ValueError(
            (
                "Ride already has a different "
                "authoritative financial "
                "allocation."
            )
        )

    cursor.execute(
        """
        INSERT INTO ride_financial_allocations (
            ride_id,
            passenger_fare,
            commission_rate,
            commission_amount,
            driver_earnings,
            currency,
            commission_policy_version,
            commission_policy_reference
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            ride_id,
            _decimal_to_storage(
                allocation.passenger_fare
            ),
            _decimal_to_storage(
                allocation.commission_rate
            ),
            _decimal_to_storage(
                allocation.commission_amount
            ),
            _decimal_to_storage(
                allocation.driver_earnings
            ),
            allocation.currency,
            (
                allocation
                .commission_policy_version
            ),
            (
                allocation
                .commission_policy_reference
            ),
        ),
    )

    return allocation