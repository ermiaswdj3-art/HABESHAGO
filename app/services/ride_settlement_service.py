"""
HABESHAGO Ride Settlement Service

Finalizes the financial settlement of a completed ride.

The service guarantees that:

- only valid rides can be settled;
- settlement is idempotent;
- authoritative Pricing Platform allocations are never
  recalculated;
- legacy callers remain temporarily supported;
- canonical Decimal financial allocations and lifecycle
  completion can be persisted together in one transaction;
- existing ride financial fields remain available as a
  compatibility mirror for existing HABESHAGO interfaces.

The canonical financial authority introduced by Commit #90
is ride_financial_allocations.

The legacy REAL-valued rides financial columns are retained
for backward compatibility during migration.
"""

from datetime import (
    datetime,
    timezone,
)

from decimal import (
    Decimal,
)

from secrets import (
    token_hex,
)

from app.constants.ride_status import (
    TRIP_COMPLETED,
)

from app.database.database import (
    create_connection,
)

from app.database.ride_financial_allocation_repository import (
    persist_ride_financial_allocation,
)

from app.models import (
    RideSettlement,
)

from app.pricing.financial import (
    FinancialAllocation,
)

from app.services.earnings_service import (
    calculate_earnings,
)


ZERO = Decimal("0.00")


def _generate_settlement_reference() -> str:
    """
    Generate a unique legacy-compatible settlement
    reference.
    """

    date_code = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d"
    )

    random_code = token_hex(
        5
    ).upper()

    return (
        f"SET-{date_code}-{random_code}"
    )


def _legacy_value_to_decimal(
    value,
) -> Decimal:
    """
    Reconstruct one legacy numeric database value as
    Decimal for compatibility validation.

    This helper does not make the legacy REAL column
    authoritative.

    It exists only so a supplied canonical allocation can
    be checked against already-stored ride values.
    """

    if value is None:
        return ZERO

    return Decimal(
        str(
            value
        )
    )


def _validate_authoritative_allocation(
    *,
    fare,
    financial_allocation: FinancialAllocation,
) -> None:
    """
    Validate that the supplied authoritative allocation
    belongs to the ride fare being settled.
    """

    if not isinstance(
        financial_allocation,
        FinancialAllocation,
    ):
        raise ValueError(
            (
                "financial_allocation must be a "
                "FinancialAllocation."
            )
        )

    stored_fare = (
        _legacy_value_to_decimal(
            fare
        )
    )

    if (
        stored_fare
        != financial_allocation.passenger_fare
    ):
        raise ValueError(
            (
                "Authoritative financial allocation "
                "passenger_fare does not match the "
                "stored ride fare."
            )
        )


def _validate_existing_settlement_matches_allocation(
    *,
    fare,
    stored_commission_rate,
    stored_commission_amount,
    stored_driver_earnings,
    financial_allocation: FinancialAllocation,
) -> None:
    """
    Ensure an authoritative allocation supplied during an
    idempotent settlement retry agrees with the already
    settled legacy compatibility values.

    This prevents a retry from silently changing financial
    authority.
    """

    _validate_authoritative_allocation(
        fare=fare,
        financial_allocation=(
            financial_allocation
        ),
    )

    stored_values = (
        _legacy_value_to_decimal(
            stored_commission_rate
        ),
        _legacy_value_to_decimal(
            stored_commission_amount
        ),
        _legacy_value_to_decimal(
            stored_driver_earnings
        ),
    )

    authoritative_values = (
        financial_allocation.commission_rate,
        financial_allocation.commission_amount,
        financial_allocation.driver_earnings,
    )

    if stored_values != authoritative_values:
        raise ValueError(
            (
                "Authoritative financial allocation "
                "does not match the existing settled "
                "ride financial values."
            )
        )


def _build_legacy_earnings_from_allocation(
    financial_allocation: FinancialAllocation,
) -> dict:
    """
    Convert one authoritative Decimal allocation into the
    legacy ride-column compatibility representation.

    Float conversion occurs only at this legacy boundary.

    The canonical allocation remains preserved separately
    as exact Decimal text.
    """

    return {
        "fare": float(
            financial_allocation.passenger_fare
        ),
        "commission_rate": float(
            financial_allocation.commission_rate
        ),
        "commission_amount": float(
            financial_allocation.commission_amount
        ),
        "driver_earnings": float(
            financial_allocation.driver_earnings
        ),
    }


def settle_completed_ride(
    ride_id: int,
    *,
    financial_allocation: (
        FinancialAllocation | None
    ) = None,
) -> RideSettlement:
    """
    Finalize one ride financially and operationally.

    The operation is idempotent.

    Two settlement paths currently exist.

    Authoritative Pricing Platform path:
        A FinancialAllocation is supplied. The allocation
        is persisted exactly and is not recalculated.

    Legacy compatibility path:
        No FinancialAllocation is supplied. Existing
        calculate_earnings behavior is temporarily
        preserved for callers not yet migrated to the
        Pricing Platform.

    A later migration can retire the legacy path after all
    HABESHAGO clients use authoritative Pricing Platform
    allocations.
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

    if (
        financial_allocation is not None
        and not isinstance(
            financial_allocation,
            FinancialAllocation,
        )
    ):
        raise ValueError(
            (
                "financial_allocation must be a "
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
                id,
                driver_id,
                fare,
                service_type,
                status,
                settlement_status,
                settled_at,
                settlement_reference,
                commission_rate,
                commission_amount,
                driver_earnings
            FROM rides
            WHERE id = ?
            """,
            (
                ride_id,
            ),
        )

        ride = cursor.fetchone()

        if ride is None:
            raise ValueError(
                "Ride not found."
            )

        (
            stored_ride_id,
            driver_id,
            fare,
            service_type,
            ride_status,
            settlement_status,
            settled_at,
            settlement_reference,
            stored_commission_rate,
            stored_commission_amount,
            stored_driver_earnings,
        ) = ride

        # ==========================================
        # IDEMPOTENT ALREADY-SETTLED PATH
        # ==========================================

        if settlement_status == "settled":
            if (
                financial_allocation
                is not None
            ):
                _validate_existing_settlement_matches_allocation(
                    fare=fare,
                    stored_commission_rate=(
                        stored_commission_rate
                    ),
                    stored_commission_amount=(
                        stored_commission_amount
                    ),
                    stored_driver_earnings=(
                        stored_driver_earnings
                    ),
                    financial_allocation=(
                        financial_allocation
                    ),
                )

                # This is idempotent when the canonical
                # allocation already exists.
                #
                # It also allows a matching authoritative
                # allocation to be safely attached during
                # a controlled retry/migration.
                persist_ride_financial_allocation(
                    cursor=cursor,
                    ride_id=stored_ride_id,
                    allocation=(
                        financial_allocation
                    ),
                )

                connection.commit()

            settlement = RideSettlement(
                ride_id=stored_ride_id,
                driver_id=driver_id,
                fare=float(
                    fare or 0
                ),
                service_type=str(
                    service_type
                    or "fuel"
                ),
                commission_rate=float(
                    stored_commission_rate
                    or 0
                ),
                commission_amount=float(
                    stored_commission_amount
                    or 0
                ),
                driver_earnings=float(
                    stored_driver_earnings
                    or 0
                ),
                settlement_status="settled",
                settled_at=settled_at,
                settlement_reference=(
                    settlement_reference
                ),
            )

            settlement.validate()

            return settlement

        # ==========================================
        # SETTLEMENT ELIGIBILITY
        # ==========================================

        if ride_status not in {
            "TRIP_STARTED",
            TRIP_COMPLETED,
        }:
            raise ValueError(
                (
                    "Only a started or completed trip "
                    "can be settled."
                )
            )

        # ==========================================
        # AUTHORITATIVE PRICING PLATFORM PATH
        # ==========================================

        if financial_allocation is not None:
            _validate_authoritative_allocation(
                fare=fare,
                financial_allocation=(
                    financial_allocation
                ),
            )

            persist_ride_financial_allocation(
                cursor=cursor,
                ride_id=stored_ride_id,
                allocation=(
                    financial_allocation
                ),
            )

            earnings = (
                _build_legacy_earnings_from_allocation(
                    financial_allocation
                )
            )

        # ==========================================
        # LEGACY COMPATIBILITY PATH
        # ==========================================

        else:
            earnings = calculate_earnings(
                float(
                    fare or 0
                ),
                str(
                    service_type
                    or "fuel"
                ),
            )

        # ==========================================
        # ATOMIC SETTLEMENT PERSISTENCE
        # ==========================================

        settlement_reference = (
            _generate_settlement_reference()
        )

        cursor.execute(
            """
            UPDATE rides
            SET
                commission_rate = ?,
                commission_amount = ?,
                driver_earnings = ?,

                settlement_status = 'settled',
                settled_at = CURRENT_TIMESTAMP,
                settlement_reference = ?,

                status = ?,
                completed_at = COALESCE(
                    completed_at,
                    CURRENT_TIMESTAMP
                )
            WHERE id = ?
              AND settlement_status != 'settled'
            """,
            (
                earnings[
                    "commission_rate"
                ],
                earnings[
                    "commission_amount"
                ],
                earnings[
                    "driver_earnings"
                ],
                settlement_reference,
                TRIP_COMPLETED,
                ride_id,
            ),
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                (
                    "Ride settlement could not "
                    "be persisted."
                )
            )

        cursor.execute(
            """
            SELECT
                settled_at
            FROM rides
            WHERE id = ?
            """,
            (
                ride_id,
            ),
        )

        settled_row = cursor.fetchone()

        connection.commit()

        settlement = RideSettlement(
            ride_id=stored_ride_id,
            driver_id=driver_id,
            fare=earnings[
                "fare"
            ],
            service_type=str(
                service_type
                or "fuel"
            ),
            commission_rate=earnings[
                "commission_rate"
            ],
            commission_amount=earnings[
                "commission_amount"
            ],
            driver_earnings=earnings[
                "driver_earnings"
            ],
            settlement_status="settled",
            settled_at=(
                settled_row[0]
                if settled_row
                else None
            ),
            settlement_reference=(
                settlement_reference
            ),
        )

        settlement.validate()

        return settlement

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()