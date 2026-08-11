"""
HABESHAGO Synchronization Update Model

Represents one platform update that must be
delivered to one or more synchronization targets.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass(slots=True)
class SynchronizationUpdate:
    """
    A platform update prepared for synchronized
    delivery across HABESHAGO interfaces.
    """

    update_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    event_id: str = ""

    event_type: str = ""

    entity: str = ""

    entity_id: int | str | None = None

    targets: tuple[str, ...] = field(default_factory=tuple)

    payload: dict[str, Any] = field(default_factory=dict)

    source: str = ""

    version: int = 1

    sequence: int = 0

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
