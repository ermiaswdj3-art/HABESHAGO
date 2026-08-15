"""
HABESHAGO Canonical Database Errors

Defines backend-neutral database exception contracts used
outside the persistence implementation boundary.
"""


class HABESHAGODatabaseError(
    RuntimeError
):
    """
    Base exception for HABESHAGO persistence failures.

    Services and clients should depend on this canonical
    error contract rather than PostgreSQL-specific errors.
    """
