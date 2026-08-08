"""
HABESHAGO Pricing Configuration Repository

Provides durable access to authoritative, versioned
PricingConfiguration records.

Financial configuration values are stored in SQLite as
exact decimal text and reconstructed as Decimal values
before entering the Pricing Domain.

This repository performs persistence only.
Pricing selection rules belong to the
Pricing Configuration Service.
"""

from datetime import (
    datetime,
)

from decimal import Decimal

from app.database.database import (
    create_connection,
)

from app.pricing.configuration import (
    PricingConfiguration,
)


def _decimal_to_storage(
    value: Decimal,
) -> str:
    """
    Convert an authoritative Decimal value to its exact
    database representation.
    """

    if not isinstance(
        value,
        Decimal,
    ):
        raise TypeError(
            "Pricing configuration money must be Decimal."
        )

    return format(
        value,
        "f",
    )


def _storage_to_decimal(
    value,
) -> Decimal:
    """
    Reconstruct an authoritative Decimal from SQLite text.
    """

    if value is None:
        raise ValueError(
            "Stored pricing decimal cannot be null."
        )

    return Decimal(
        str(value)
    )


def _datetime_to_storage(
    value: datetime | None,
) -> str | None:
    """
    Convert one timezone-aware datetime to ISO-8601 text.
    """

    if value is None:
        return None

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            "Pricing configuration datetime "
            "must be timezone-aware."
        )

    return value.isoformat()


def _storage_to_datetime(
    value,
) -> datetime | None:
    """
    Reconstruct one datetime from stored ISO-8601 text.
    """

    if value is None:
        return None

    return datetime.fromisoformat(
        str(value)
    )


def _row_to_configuration(
    row,
) -> PricingConfiguration | None:
    """
    Convert one pricing configuration row into the
    authoritative PricingConfiguration domain model.
    """

    if row is None:
        return None

    return PricingConfiguration(
        configuration_id=row[0],
        configuration_version=row[1],
        city=row[2],
        service_type=row[3],
        ride_category=row[4],
        currency=row[5],
        base_fare=(
            _storage_to_decimal(
                row[6]
            )
        ),
        price_per_km=(
            _storage_to_decimal(
                row[7]
            )
        ),
        price_per_minute=(
            _storage_to_decimal(
                row[8]
            )
        ),
        waiting_price_per_minute=(
            _storage_to_decimal(
                row[9]
            )
        ),
        minimum_fare=(
            _storage_to_decimal(
                row[10]
            )
        ),
        rounding_policy=row[11],
        rounding_multiple=(
            _storage_to_decimal(
                row[12]
            )
        ),
        pricing_policy=row[13],
        surge_policy=row[14],
        effective_from=(
            _storage_to_datetime(
                row[15]
            )
        ),
        effective_until=(
            _storage_to_datetime(
                row[16]
            )
        ),
        is_active=bool(
            row[17]
        ),
        created_at=(
            _storage_to_datetime(
                row[18]
            )
            if row[18] is not None
            else None
        ),
        updated_at=(
            _storage_to_datetime(
                row[19]
            )
            if row[19] is not None
            else None
        ),
    )


def create_pricing_configuration(
    configuration: PricingConfiguration,
) -> PricingConfiguration:
    """
    Persist one immutable PricingConfiguration version.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO pricing_configurations (
                configuration_version,
                city,
                service_type,
                ride_category,
                currency,
                base_fare,
                price_per_km,
                price_per_minute,
                waiting_price_per_minute,
                minimum_fare,
                rounding_policy,
                rounding_multiple,
                pricing_policy,
                surge_policy,
                effective_from,
                effective_until,
                is_active,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?,
                ?,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            )
            """,
            (
                configuration.configuration_version,
                configuration.city,
                configuration.service_type,
                configuration.ride_category,
                configuration.currency,
                _decimal_to_storage(
                    configuration.base_fare
                ),
                _decimal_to_storage(
                    configuration.price_per_km
                ),
                _decimal_to_storage(
                    configuration.price_per_minute
                ),
                _decimal_to_storage(
                    configuration.waiting_price_per_minute
                ),
                _decimal_to_storage(
                    configuration.minimum_fare
                ),
                configuration.rounding_policy,
                _decimal_to_storage(
                    configuration.rounding_multiple
                ),
                configuration.pricing_policy,
                configuration.surge_policy,
                _datetime_to_storage(
                    configuration.effective_from
                ),
                _datetime_to_storage(
                    configuration.effective_until
                ),
                int(
                    configuration.is_active
                ),
            ),
        )

        configuration_id = (
            cursor.lastrowid
        )

        cursor.execute(
            """
            SELECT
                id,
                configuration_version,
                city,
                service_type,
                ride_category,
                currency,
                base_fare,
                price_per_km,
                price_per_minute,
                waiting_price_per_minute,
                minimum_fare,
                rounding_policy,
                rounding_multiple,
                pricing_policy,
                surge_policy,
                effective_from,
                effective_until,
                is_active,
                created_at,
                updated_at
            FROM pricing_configurations
            WHERE id = ?
            """,
            (
                configuration_id,
            ),
        )

        row = cursor.fetchone()

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    stored = _row_to_configuration(
        row
    )

    if stored is None:
        raise RuntimeError(
            "Stored PricingConfiguration could not "
            "be reloaded."
        )

    return stored


def get_pricing_configuration_by_version(
    configuration_version: str,
) -> PricingConfiguration | None:
    """
    Return one exact PricingConfiguration version.
    """

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            configuration_version,
            city,
            service_type,
            ride_category,
            currency,
            base_fare,
            price_per_km,
            price_per_minute,
            waiting_price_per_minute,
            minimum_fare,
            rounding_policy,
            rounding_multiple,
            pricing_policy,
            surge_policy,
            effective_from,
            effective_until,
            is_active,
            created_at,
            updated_at
        FROM pricing_configurations
        WHERE configuration_version = ?
        LIMIT 1
        """,
        (
            configuration_version,
        ),
    )

    row = cursor.fetchone()

    connection.close()

    return _row_to_configuration(
        row
    )


def list_pricing_configurations(
    *,
    city: str | None = None,
    service_type: str | None = None,
    ride_category: str | None = None,
    is_active: bool | None = None,
) -> list[PricingConfiguration]:
    """
    Return PricingConfiguration history with optional
    scope filters.

    Effective-time selection is intentionally not handled
    here.
    """

    conditions = []
    parameters = []

    if city is not None:
        conditions.append(
            "city = ?"
        )
        parameters.append(
            city
        )

    if service_type is not None:
        conditions.append(
            "service_type = ?"
        )
        parameters.append(
            service_type
        )

    if ride_category is not None:
        conditions.append(
            "ride_category = ?"
        )
        parameters.append(
            ride_category
        )

    if is_active is not None:
        conditions.append(
            "is_active = ?"
        )
        parameters.append(
            int(
                is_active
            )
        )

    where_clause = ""

    if conditions:
        where_clause = (
            "WHERE "
            + " AND ".join(
                conditions
            )
        )

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        f"""
        SELECT
            id,
            configuration_version,
            city,
            service_type,
            ride_category,
            currency,
            base_fare,
            price_per_km,
            price_per_minute,
            waiting_price_per_minute,
            minimum_fare,
            rounding_policy,
            rounding_multiple,
            pricing_policy,
            surge_policy,
            effective_from,
            effective_until,
            is_active,
            created_at,
            updated_at
        FROM pricing_configurations
        {where_clause}
        ORDER BY
            effective_from ASC,
            id ASC
        """,
        tuple(
            parameters
        ),
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        _row_to_configuration(
            row
        )
        for row in rows
    ]


def set_pricing_configuration_active(
    *,
    configuration_version: str,
    is_active: bool,
) -> PricingConfiguration:
    """
    Change only the administrative active flag for one
    stored configuration version.

    Historical pricing values remain immutable.
    """

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE pricing_configurations
            SET
                is_active = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE configuration_version = ?
            """,
            (
                int(
                    is_active
                ),
                configuration_version,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError(
                "Pricing configuration not found."
            )

        cursor.execute(
            """
            SELECT
                id,
                configuration_version,
                city,
                service_type,
                ride_category,
                currency,
                base_fare,
                price_per_km,
                price_per_minute,
                waiting_price_per_minute,
                minimum_fare,
                rounding_policy,
                rounding_multiple,
                pricing_policy,
                surge_policy,
                effective_from,
                effective_until,
                is_active,
                created_at,
                updated_at
            FROM pricing_configurations
            WHERE configuration_version = ?
            """,
            (
                configuration_version,
            ),
        )

        row = cursor.fetchone()

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    configuration = (
        _row_to_configuration(
            row
        )
    )

    if configuration is None:
        raise RuntimeError(
            "Pricing configuration could not "
            "be loaded after update."
        )

    return configuration