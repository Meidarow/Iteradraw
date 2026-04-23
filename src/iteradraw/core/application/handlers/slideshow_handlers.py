from iteradraw.core.application.commands.slideshow_commands import \
    StartTimedSlideshowCommand, NextSlideCommand, \
    PreviousSlideCommand
from iteradraw.core.infrastructure.buses.event_bus import EventBus
from iteradraw.interfaces import CommandHandler


class StartTimedSlideshowCommandHandler(CommandHandler[StartTimedSlideshowCommand]):
    command_type = StartTimedSlideshowCommand

    def __init__(self, event_bus: EventBus, **_):
        self.event_bus = event_bus

    def handle(self, command: StartTimedSlideshowCommand):
        """Process:
        verify database;
        check stale folders
        crawl stale folders
        Dtabase ready
        command playlist service to build playlist
        start timed slideshow"""
        pass

class NextSlideCommandHandler(CommandHandler[NextSlideCommand]):
    def __init__(self, event_bus: EventBus, **_):
        pass

    def handle(self, command: NextSlideCommand):
        pass


class PreviousSlideCommandHandler(CommandHandler[PreviousSlideCommand]):
    def __init__(self, event_bus: EventBus, **_):
        pass

    def handle(self, command: PreviousSlideCommand):
        pass