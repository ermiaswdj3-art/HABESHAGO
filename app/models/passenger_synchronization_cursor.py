"""
HABESHAGO Passenger Synchronization Cursor Model

Represents one passenger's synchronization progress
through ordered HABESHAGO synchronization updates.

Commit #110 purpose:

- record the last synchronization sequence processed
  for one canonical passenger;
- support deterministic replay resumption;
- prevent synchronization progress from moving backward.

This model does not acknowledge updates and does not
modify canonical Ride state.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class PassengerSynchronizationCursor:
    """
    Immutable snapshot of one passenger's
    synchronization progress.
    """

    passenger_id: int

    last_sequence: int = 0

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )
