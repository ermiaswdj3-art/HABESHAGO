"""
HABESHAGO PostgreSQL Connection Adapter

Provides the production PostgreSQL connection boundary.

Repositories and services must continue using the shared
create_connection() authority rather than connecting to
PostgreSQL directly.
"""

import psycopg

from app.database.backend import (
    get_database_url,
)

from app.database.errors import (
    HABESHAGODatabaseError,
)



class PostgreSQLConnectionError(
    HABESHAGODatabaseError
):
    """
    Raised when PostgreSQL configuration or connection fails.
    """


class PostgreSQLRuntimeError(
    HABESHAGODatabaseError
):
    """
    Raised when an established PostgreSQL connection fails
    during database execution, fetching, or transaction work.
    """


def create_postgresql_connection():
    """
    Create one HABESHAGO PostgreSQL connection.

    DATABASE_URL remains the canonical production
    connection configuration.
    """

    database_url = get_database_url()

    if not database_url:
        raise PostgreSQLConnectionError(
            "DATABASE_URL is required for "
            "HABESHAGO PostgreSQL."
        )

    try:
        raw_connection = psycopg.connect(
            database_url,
        )

        return PostgreSQLCompatibleConnection(
            raw_connection
        )

    except psycopg.Error as exc:
        raise PostgreSQLConnectionError(
            "Unable to connect to the HABESHAGO "
            "PostgreSQL database."
        ) from exc

def translate_sql_parameters(
    statement: str,
) -> str:
    """
    Translate HABESHAGO's canonical qmark SQL parameter
    style into PostgreSQL/psycopg parameter markers.

    Example:

        WHERE driver_id = ?
        WHERE driver_id = %s

    Translation intentionally operates only outside
    quoted SQL string literals.
    """

    if not isinstance(statement, str):
        raise TypeError(
            "SQL statement must be a string."
        )

    result = []

    in_single_quote = False
    in_double_quote = False

    index = 0

    while index < len(statement):

        character = statement[index]

        if character == "'" and not in_double_quote:

            # SQL escapes a single quote inside a string
            # literal by doubling it: ''
            if (
                in_single_quote
                and index + 1 < len(statement)
                and statement[index + 1] == "'"
            ):
                result.append("''")
                index += 2
                continue

            in_single_quote = (
                not in_single_quote
            )

            result.append(character)
            index += 1
            continue

        if character == '"' and not in_single_quote:

            # Preserve doubled quoted-identifier quotes.
            if (
                in_double_quote
                and index + 1 < len(statement)
                and statement[index + 1] == '"'
            ):
                result.append('""')
                index += 2
                continue

            in_double_quote = (
                not in_double_quote
            )

            result.append(character)
            index += 1
            continue

        if (
            character == "?"
            and not in_single_quote
            and not in_double_quote
        ):
            result.append("%s")

        else:
            result.append(character)

        index += 1

    return "".join(result)



def translate_sqlite_insert_or_ignore(
    statement: str,
) -> str:
    """
    Translate SQLite INSERT OR IGNORE into PostgreSQL's
    equivalent conflict-tolerant INSERT form.

    HABESHAGO currently uses this construct only for
    idempotent canonical registration/backfill inserts.

    SQLite:

        INSERT OR IGNORE INTO ...

    PostgreSQL:

        INSERT INTO ...
        ...
        ON CONFLICT DO NOTHING
    """

    if not isinstance(statement, str):
        raise TypeError(
            "SQL statement must be a string."
        )

    import re

    translated, count = re.subn(
        r"""
        ^(\s*)
        INSERT
        \s+OR\s+IGNORE
        \s+INTO
        """,
        r"\1INSERT INTO",
        statement,
        count=1,
        flags=(
            re.IGNORECASE
            | re.VERBOSE
        ),
    )

    if count == 0:
        return statement

    translated = (
        translated.rstrip()
        .rstrip(";")
        + " ON CONFLICT DO NOTHING"
    )

    return translated


def _is_sqlite_foreign_keys_enable_pragma(
    statement: str,
) -> bool:
    """
    Return True only for SQLite's runtime foreign-key
    enablement statement:

        PRAGMA foreign_keys = ON

    PostgreSQL foreign-key constraints are enforced by
    the database schema and require no equivalent runtime
    enablement command.

    Other PRAGMA statements are intentionally not accepted.
    """

    if not isinstance(statement, str):
        return False

    import re

    return bool(
        re.fullmatch(
            r"""
            \s*
            PRAGMA
            \s+
            foreign_keys
            \s*=\s*
            ON
            \s*;?
            \s*
            """,
            statement,
            flags=(
                re.IGNORECASE
                | re.VERBOSE
            ),
        )
    )


def _is_insert_statement(
    statement: str,
) -> bool:
    """
    Return True when the SQL statement begins with INSERT.

    This supports DB-API lastrowid compatibility for
    HABESHAGO repositories when PostgreSQL is active.
    """

    if not isinstance(statement, str):
        return False

    return (
        statement
        .lstrip()
        .upper()
        .startswith("INSERT ")
    )


def _has_returning_clause(
    statement: str,
) -> bool:
    """
    Return True when a SQL statement already contains
    an explicit PostgreSQL RETURNING clause.
    """

    if not isinstance(statement, str):
        return False

    return (
        " RETURNING "
        in (
            " "
            + statement.upper()
            + " "
        )
    )

class PostgreSQLCompatibleCursor:
    """
    DB-API compatibility cursor for HABESHAGO PostgreSQL.

    Existing HABESHAGO repositories use SQLite qmark
    parameter markers. This wrapper translates those
    statements before delegating to psycopg.

    Result fetching, row counts, and normal cursor
    behavior continue to come from the real psycopg
    cursor.
    """

    def __init__(
        self,
        cursor,
    ):
        self._cursor = cursor
        self._lastrowid = None

    def execute(
        self,
        statement,
        parameters=None,
    ):
        translated = translate_sql_parameters(
            statement
        )

        translated = (
            translate_sqlite_datetime_functions(
                translated
            )
        )

        translated = (
            translate_sqlite_insert_or_ignore(
                translated
            )
        )

        self._lastrowid = None

        if _is_sqlite_foreign_keys_enable_pragma(
            translated
        ):
            return self

        capture_insert_id = (
            _is_insert_statement(
                translated
            )
            and not _has_returning_clause(
                translated
            )
        )

        if capture_insert_id:
            translated = (
                translated.rstrip()
                .rstrip(";")
                + " RETURNING id"
            )

        try:
            if parameters is None:
                self._cursor.execute(
                    translated
                )
            else:
                self._cursor.execute(
                    translated,
                    parameters,
                )

            if capture_insert_id:
                returned_row = (
                    self._cursor.fetchone()
                )

        except psycopg.Error as exc:
            raise PostgreSQLRuntimeError(
                "HABESHAGO PostgreSQL statement "
                "execution failed."
            ) from exc

        if capture_insert_id:

            if returned_row is not None:
                self._lastrowid = (
                    returned_row[0]
                )

        return self

    @property
    def lastrowid(self):
        """
        Return the generated integer identifier from the
        most recent HABESHAGO INSERT operation.

        This preserves the DB-API contract currently used
        by SQLite-backed HABESHAGO repositories.
        """

        return self._lastrowid

    def fetchone(self):
        try:
            return self._cursor.fetchone()

        except psycopg.Error as exc:
            raise PostgreSQLRuntimeError(
                "HABESHAGO PostgreSQL fetchone "
                "operation failed."
            ) from exc

    def fetchall(self):
        try:
            return self._cursor.fetchall()

        except psycopg.Error as exc:
            raise PostgreSQLRuntimeError(
                "HABESHAGO PostgreSQL fetchall "
                "operation failed."
            ) from exc

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        return self._cursor.close()

    def __iter__(self):
        return iter(
            self._cursor
        )

    def __enter__(self):
        self._cursor.__enter__()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return self._cursor.__exit__(
            exc_type,
            exc_value,
            traceback,
        )


class PostgreSQLCompatibleConnection:
    """
    HABESHAGO-compatible PostgreSQL connection wrapper.

    The wrapper preserves the connection API already used
    by existing repositories while ensuring every cursor
    receives PostgreSQL SQL compatibility translation.
    """

    def __init__(
        self,
        connection,
    ):
        self._connection = connection

    def cursor(self, *args, **kwargs):
        try:
            cursor = self._connection.cursor(
                *args,
                **kwargs,
            )

        except psycopg.Error as exc:
            raise PostgreSQLRuntimeError(
                "Unable to create HABESHAGO "
                "PostgreSQL cursor."
            ) from exc

        return PostgreSQLCompatibleCursor(
            cursor
        )

    def commit(self):
        try:
            return self._connection.commit()

        except psycopg.Error as exc:
            raise PostgreSQLRuntimeError(
                "HABESHAGO PostgreSQL commit failed."
            ) from exc

    def rollback(self):
        try:
            return self._connection.rollback()

        except psycopg.Error as exc:
            raise PostgreSQLRuntimeError(
                "HABESHAGO PostgreSQL rollback failed."
            ) from exc

    def close(self):
        try:
            return self._connection.close()

        except psycopg.Error as exc:
            raise PostgreSQLRuntimeError(
                "HABESHAGO PostgreSQL close failed."
            ) from exc

    def __enter__(self):
        self._connection.__enter__()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return self._connection.__exit__(
            exc_type,
            exc_value,
            traceback,
        )


def translate_sqlite_datetime_functions(
    statement: str,
) -> str:
    """
    Translate the simple SQLite DATETIME forms currently used
    by HABESHAGO ride-offer lifecycle SQL into PostgreSQL.

    Supported forms:

        DATETIME('now')
            -> CURRENT_TIMESTAMP

        DATETIME(column_or_parameter)
            -> CAST(column_or_parameter AS TIMESTAMP)

    Complex SQLite modifier forms such as:

        DATETIME('now', 'localtime', ?)

    are intentionally left unchanged. They require explicit
    semantic handling rather than unsafe textual rewriting.
    """

    if not isinstance(statement, str):
        raise TypeError(
            "SQL statement must be a string."
        )

    import re

    translated = re.sub(
        r"""DATETIME\s*\(\s*['"]now['"]\s*\)""",
        "CURRENT_TIMESTAMP",
        statement,
        flags=re.IGNORECASE,
    )

    translated = re.sub(
        r"""
        DATETIME
        \s*\(
        \s*
        (
            %s
            |
            [A-Za-z_][A-Za-z0-9_.]*
        )
        \s*
        \)
        """,
        r"CAST(\1 AS TIMESTAMP)",
        translated,
        flags=(
            re.IGNORECASE
            | re.VERBOSE
        ),
    )

    # HABESHAGO canonical persistence time is UTC.
    #
    # Historical SQLite health SQL uses:
    #
    #     DATETIME(
    #         'now',
    #         'localtime',
    #         %s
    #     )
    #
    # PostgreSQL must not inherit server-local time as
    # platform truth. Preserve the existing interval
    # parameter while evaluating against the canonical
    # PostgreSQL current timestamp.
    translated = re.sub(
        r"""
        DATETIME
        \s*\(
        \s*['"]now['"]
        \s*,\s*
        ['"]localtime['"]
        \s*,\s*
        %s
        \s*\)
        """,
        (
            "CURRENT_TIMESTAMP "
            "+ CAST(%s AS INTERVAL)"
        ),
        translated,
        flags=(
            re.IGNORECASE
            | re.VERBOSE
        ),
    )

    # Historical SQLite operational-summary SQL compares
    # canonical timestamps using:
    #
    #     DATE(value) = DATE('now', 'localtime')
    #
    # HABESHAGO persistence time is canonical UTC. PostgreSQL
    # therefore evaluates the same platform-day contract using
    # CAST(value AS DATE) and CURRENT_DATE rather than inheriting
    # SQLite process-local time semantics.
    translated = re.sub(
        r"""
        DATE
        \s*\(
        \s*['"]now['"]
        \s*,\s*
        ['"]localtime['"]
        \s*\)
        """,
        "CURRENT_DATE",
        translated,
        flags=(
            re.IGNORECASE
            | re.VERBOSE
        ),
    )

    translated = re.sub(
        r"""
        DATE
        \s*\(
        \s*
        (
            COALESCE
            \s*\(
                [^()]+
            \)
            |
            %s
            |
            [A-Za-z_][A-Za-z0-9_.]*
        )
        \s*
        \)
        """,
        r"CAST(\1 AS DATE)",
        translated,
        flags=(
            re.IGNORECASE
            | re.VERBOSE
        ),
    )

    return translated

