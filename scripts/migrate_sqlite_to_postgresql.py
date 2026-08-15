"""
HABESHAGO SQLite -> PostgreSQL Controlled Migration

Copies the current canonical HABESHAGO business records from
SQLite into an EMPTY PostgreSQL target.

Non-negotiable migration rules:

- Preserve canonical primary-key IDs.
- Preserve business identities and foreign keys.
- Normalize SQLite timestamp strings for PostgreSQL.
- Migrate in foreign-key-safe order.
- Run inside one PostgreSQL transaction.
- Roll back the complete migration on any failure.
- Synchronize PostgreSQL identity sequences after explicit-ID import.
- Never delete or mutate SQLite source records.
"""


from datetime import datetime

from app.database.database import (
    create_connection as create_sqlite_connection,
)

from app.database.postgresql import (
    create_postgresql_connection,
)


MIGRATION_TABLES = [
    "passengers",
    "drivers",
    "vehicles",
    "rides",
    "ride_financial_allocations",
    "ride_offers",
    "driver_admin_actions",
    "pricing_configurations",
    "payment_obligations",
    "payment_requests",
    "payment_intents",
    "payment_transactions",
    "payment_verifications",
    "payment_reconciliations",
    "passenger_places",
]


EXPECTED_SOURCE_ROWS = {
    "passengers": 4,
    "drivers": 2,
    "vehicles": 2,
    "rides": 44,
    "ride_financial_allocations": 0,
    "ride_offers": 0,
    "driver_admin_actions": 0,
    "pricing_configurations": 4,
    "payment_obligations": 0,
    "payment_requests": 0,
    "payment_intents": 0,
    "payment_transactions": 0,
    "payment_verifications": 0,
    "payment_reconciliations": 0,
    "passenger_places": 6,
}


class HABESHAGOMigrationError(
    RuntimeError
):
    """
    Raised when controlled HABESHAGO migration cannot
    safely continue.
    """


def normalize_timestamp(
    value,
):
    """
    Normalize one SQLite timestamp value for PostgreSQL.
    """

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value

    if not isinstance(
        value,
        str,
    ):
        raise HABESHAGOMigrationError(
            "Unexpected timestamp value type: "
            f"{type(value).__name__}"
        )

    clean = value.strip()

    candidates = [
        clean,
        clean.replace(
            "Z",
            "+00:00",
        ),
    ]

    for candidate in candidates:

        try:
            return datetime.fromisoformat(
                candidate
            )

        except ValueError:
            continue

    raise HABESHAGOMigrationError(
        "Unable to normalize timestamp: "
        f"{value!r}"
    )


def get_postgresql_column_contract(
    cursor,
    table,
):
    """
    Return PostgreSQL column metadata in ordinal order.
    """

    cursor.execute(
        """
        SELECT
            column_name,
            data_type,
            is_identity
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = ?
        ORDER BY ordinal_position
        """,
        (
            table,
        ),
    )

    return cursor.fetchall()


def get_sqlite_rows(
    cursor,
    table,
):
    """
    Return SQLite column names and all canonical rows.
    """

    cursor.execute(
        f"PRAGMA table_info({table})"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    cursor.execute(
        f"SELECT * FROM {table}"
    )

    rows = cursor.fetchall()

    return (
        columns,
        rows,
    )


def assert_postgresql_target_empty(
    cursor,
):
    """
    Refuse migration unless every target table is empty.
    """

    non_empty = []

    for table in MIGRATION_TABLES:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        if count:
            non_empty.append(
                (
                    table,
                    count,
                )
            )

    if non_empty:
        raise HABESHAGOMigrationError(
            "PostgreSQL migration target is not empty: "
            f"{non_empty}"
        )


def migrate_table(
    sqlite_cursor,
    postgres_cursor,
    table,
):
    """
    Copy one canonical HABESHAGO table while preserving IDs.
    """

    columns, rows = get_sqlite_rows(
        sqlite_cursor,
        table,
    )

    expected = EXPECTED_SOURCE_ROWS[
        table
    ]

    if len(rows) != expected:
        raise HABESHAGOMigrationError(
            f"{table}: expected {expected} source rows, "
            f"found {len(rows)}."
        )

    if not rows:
        return 0

    contract = (
        get_postgresql_column_contract(
            postgres_cursor,
            table,
        )
    )

    postgres_columns = [
        row[0]
        for row in contract
    ]

    # Migration correctness depends on semantic column
    # identity, not physical column position.
    #
    # SQLite legacy migrations may have appended columns
    # in an order different from the canonical PostgreSQL
    # fresh schema. INSERT statements below explicitly name
    # every source column, so different physical ordering is
    # safe when both engines expose the same column set.
    if (
        len(columns)
        != len(postgres_columns)
        or set(columns)
        != set(postgres_columns)
    ):
        missing_in_postgresql = sorted(
            set(columns)
            - set(postgres_columns)
        )

        unexpected_in_postgresql = sorted(
            set(postgres_columns)
            - set(columns)
        )

        raise HABESHAGOMigrationError(
            f"{table}: SQLite/PostgreSQL column surface "
            "does not match. "
            f"Missing in PostgreSQL: "
            f"{missing_in_postgresql}. "
            f"Unexpected in PostgreSQL: "
            f"{unexpected_in_postgresql}."
        )

    postgres_types = {
        row[0]: row[1]
        for row in contract
    }

    # Row values remain in SQLite source-column order.
    # Therefore timestamp normalization must also be
    # calculated from SQLite column positions by name,
    # rather than PostgreSQL physical positions.
    timestamp_indexes = {
        index
        for index, column in enumerate(
            columns
        )
        if postgres_types[column] in {
            "timestamp without time zone",
            "timestamp with time zone",
        }
    }

    placeholders = ", ".join(
        "?"
        for _ in columns
    )

    column_sql = ", ".join(
        columns
    )

    statement = (
        f"INSERT INTO {table} "
        f"({column_sql}) "
        f"VALUES ({placeholders})"
    )

    migrated = 0

    for row in rows:

        normalized = list(
            row
        )

        for index in timestamp_indexes:

            normalized[index] = (
                normalize_timestamp(
                    normalized[index]
                )
            )

        postgres_cursor.execute(
            statement,
            tuple(
                normalized
            ),
        )

        migrated += 1

    return migrated


def synchronize_identity(
    cursor,
    table,
):
    """
    Synchronize one PostgreSQL identity sequence after
    explicit canonical IDs have been imported.
    """

    cursor.execute(
        f"SELECT COALESCE(MAX(id), 0) FROM {table}"
    )

    maximum_id = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT pg_get_serial_sequence(?, 'id')
        """,
        (
            table,
        ),
    )

    sequence_name = cursor.fetchone()[0]

    if not sequence_name:
        raise HABESHAGOMigrationError(
            f"{table}: PostgreSQL identity sequence "
            "could not be resolved."
        )

    if maximum_id > 0:

        cursor.execute(
            """
            SELECT setval(
                ?,
                ?,
                true
            )
            """,
            (
                sequence_name,
                maximum_id,
            ),
        )

    else:

        cursor.execute(
            """
            SELECT setval(
                ?,
                1,
                false
            )
            """,
            (
                sequence_name,
            ),
        )

    return maximum_id


def migrate():
    """
    Execute the complete controlled HABESHAGO migration.
    """

    sqlite_connection = (
        create_sqlite_connection()
    )

    postgres_connection = (
        create_postgresql_connection()
    )

    sqlite_cursor = (
        sqlite_connection.cursor()
    )

    postgres_cursor = (
        postgres_connection.cursor()
    )

    migrated_counts = {}
    identity_maxima = {}

    try:

        assert_postgresql_target_empty(
            postgres_cursor
        )

        for table in MIGRATION_TABLES:

            count = migrate_table(
                sqlite_cursor,
                postgres_cursor,
                table,
            )

            migrated_counts[
                table
            ] = count

            print(
                f"MIGRATED {table}: {count}"
            )

        total = sum(
            migrated_counts.values()
        )

        if total != 62:
            raise HABESHAGOMigrationError(
                "Expected exactly 62 migrated rows, "
                f"got {total}."
            )

        for table in MIGRATION_TABLES:

            identity_maxima[
                table
            ] = synchronize_identity(
                postgres_cursor,
                table,
            )

        postgres_connection.commit()

        return {
            "migrated_counts":
                migrated_counts,

            "total_rows":
                total,

            "identity_maxima":
                identity_maxima,
        }

    except Exception:

        postgres_connection.rollback()

        raise

    finally:

        sqlite_cursor.close()
        sqlite_connection.close()

        postgres_cursor.close()
        postgres_connection.close()


if __name__ == "__main__":

    result = migrate()

    print()
    print(
        "Migration result:"
    )

    print(
        result
    )
