"""
HABESHAGO Database Backend Configuration

Defines the canonical database backend selection contract.

Development currently defaults to SQLite.

Future production deployments may select PostgreSQL through
environment configuration without allowing individual services,
repositories, Telegram clients, Mini Apps, or future clients to
choose their own persistence authority.
"""

import os

from dotenv import load_dotenv


# Load HABESHAGO project environment configuration before
# resolving the canonical persistence authority.
#
# This keeps database backend selection independent from
# Telegram, Mini App, or other client-specific imports.
load_dotenv()


SQLITE_BACKEND = "sqlite"
POSTGRESQL_BACKEND = "postgresql"

SUPPORTED_DATABASE_BACKENDS = {
    SQLITE_BACKEND,
    POSTGRESQL_BACKEND,
}


class DatabaseConfigurationError(
    RuntimeError
):
    """
    Raised when HABESHAGO database configuration is invalid.
    """


def get_database_backend() -> str:
    """
    Return the configured HABESHAGO database backend.

    SQLite remains the safe development default.
    """

    backend = (
        os.getenv(
            "HABESHAGO_DATABASE_BACKEND",
            SQLITE_BACKEND,
        )
        .strip()
        .lower()
    )

    aliases = {
        "postgres": POSTGRESQL_BACKEND,
        "postgresql": POSTGRESQL_BACKEND,
        "sqlite": SQLITE_BACKEND,
    }

    normalized = aliases.get(
        backend,
        backend,
    )

    if (
        normalized
        not in SUPPORTED_DATABASE_BACKENDS
    ):
        raise DatabaseConfigurationError(
            "Unsupported HABESHAGO database "
            f"backend: {backend!r}"
        )

    return normalized


def get_database_url() -> str | None:
    """
    Return the configured production database URL.

    No URL is required while SQLite is the active backend.
    """

    value = os.getenv(
        "DATABASE_URL"
    )

    if value is None:
        return None

    normalized = value.strip()

    return normalized or None


def validate_database_configuration():
    """
    Validate the selected HABESHAGO persistence configuration.
    """

    backend = get_database_backend()

    if (
        backend == POSTGRESQL_BACKEND
        and not get_database_url()
    ):
        raise DatabaseConfigurationError(
            "DATABASE_URL is required when "
            "HABESHAGO_DATABASE_BACKEND=postgresql."
        )

    return backend
