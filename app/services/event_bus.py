"""
HABESHAGO Event Bus

The Event Bus keeps track of
listeners interested in platform
events.
"""

from collections import defaultdict
from typing import Callable

from app.models.event import Event

_LISTENERS: dict[str, list[Callable[[Event], None]]] = defaultdict(list)


def subscribe(
    event_type: str,
    listener: Callable[[Event], None],
) -> None:
    """
    Register an event listener.
    """

    _LISTENERS[event_type].append(listener)


def get_listeners(
    event_type: str,
) -> list[Callable[[Event], None]]:
    """
    Return listeners interested in
    this event.
    """

    return _LISTENERS.get(
        event_type,
        [],
    )
