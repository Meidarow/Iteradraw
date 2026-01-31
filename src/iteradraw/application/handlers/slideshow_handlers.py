from typing import TYPE_CHECKING

from iteradraw.application.commands.slideshow_commands import \
    DecodeImageCommand
from iteradraw.interfaces import Command

if TYPE_CHECKING:
    from iteradraw.infrastructure.buses.event_bus import EventBus
    from iteradraw.application.services.decoder_service import DecoderService


class NextSlideCommandHandler(Command):
    ...


class PreviousSlideCommandHandler(Command):
    ...


class DecodeImageCommandHandler(Command):
    def __init__(self, service: DecoderService, event_bus: EventBus):
        self.service = service
        self.event_bus = event_bus

    def handle(self, command: DecodeImageCommand):
        self.service.decode_image(command.image_path)
        evt =
        self.event_bus.publish(evt)