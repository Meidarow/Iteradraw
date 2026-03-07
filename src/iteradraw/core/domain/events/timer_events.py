from dataclasses import dataclass

from iteradraw.interfaces import Event

@dataclass(frozen=True)
class TimerAdded(Event):
    ...


@dataclass(frozen=True)
class TimerRemoved(Event):
    ...