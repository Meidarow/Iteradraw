from typing import TYPE_CHECKING

from iteradraw.core.application.commands.slideshow_commands import \
    DecodeImageCommand, StartTimedSlideshowCommand, NextSlideCommand, PreviousSlideCommand
from iteradraw.interfaces import CommandHandler

if TYPE_CHECKING:
    from iteradraw.core.infrastructure import EventBus

class StartTimedSlideshowCommandHandler(CommandHandler[StartTimedSlideshowCommand]):
    def __init__(self, event_bus: EventBus):
        pass

    def handle(self, command: StartTimedSlideshowCommand):
        """Process:
        verify database;
        check stale folders
        crawl stale folders
        Dtabase ready
        command playlist service to build playlist
        start timed slideshow"""

class NextSlideCommandHandler(CommandHandler[NextSlideCommand]):
    def __init__(self, event_bus: EventBus):
        pass

    def handle(self, command: DecodeImageCommand):
        pass


class PreviousSlideCommandHandler(CommandHandler[PreviousSlideCommand]):
    def __init__(self, event_bus: EventBus):
        pass

    def handle(self, command: DecodeImageCommand):
        pass


class DecodeImageCommandHandler(CommandHandler[DecodeImageCommand]):
    def __init__(self, event_bus: EventBus):
        pass

    def handle(self, command: DecodeImageCommand):
        pass