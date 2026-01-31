from dataclasses import dataclass
from typing import Optional

from iteradraw.interfaces import Command

@dataclass(frozen=True)
class NextSlideCommand(Command):
    ...

@dataclass(frozen=True)
class PreviousSlideCommand(Command):
    ...

@dataclass(frozen=True)
class DecodeImageCommand(Command):
    """
    Intent: Asks for compressed image to be decoded into pixel data.
    Triggered by:
        1. Renderer: on Cache miss
        2. PlaylistService: when preloading thumbnails at start up.
    """
    image_path: str
    is_priority: bool = False