from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass(slots=True)
class Event:
    """
    HABESHAGO platform event.

    Every engine communicates by publishing
    Event objects.
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    event_type: str = ""

    entity: str = ""

    payload: dict[str, Any] = field(default_factory=dict)

    source: str = ""

    version: int = 1

    created_at: datetime = field(default_factory=datetime.utcnow)
