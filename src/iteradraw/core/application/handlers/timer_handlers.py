from iteradraw.core.application.commands.timer_commands import AddTimerCommand, RemoveTimerCommand
from iteradraw.interfaces import Command, CommandHandler


class AddTimerCommandHandler(CommandHandler[AddTimerCommand]):
    def __init__(self):
        pass
    def handle(self, command: Command) -> Command:
        pass

class RemoveTimerCommandHandler(CommandHandler[RemoveTimerCommand]):
    def __init__(self):
        pass
    def handle(self, command: Command) -> Command:
        pass
