from dataclasses import dataclass

from iteradraw.interfaces import Command


@dataclass(frozen=True)
class StartTimedSlideshowCommand(Command):
    """
    Attributes:
        timer: int
        shuffle: bool
    """
    timer: int
    shuffle: bool

class StartComposedSlideshowCommand(Command):
    ...

@dataclass(frozen=True)
class NextSlideCommand(Command):
    ...

@dataclass(frozen=True)
class PreviousSlideCommand(Command):
    ...
