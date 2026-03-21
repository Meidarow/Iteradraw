from dataclasses import dataclass

from iteradraw.core.domain.models.folder import FolderSet, Folder
from iteradraw.interfaces import Event


@dataclass(frozen=True)
class TimedSlideshowRequested(Event):
    folders: FolderSet
    timer: int

@dataclass(frozen=True)
class DatabaseVerified(Event):
    success: bool


@dataclass(frozen=True)
class CrawlingStarted(Event):
    folder: Folder

@dataclass(frozen=True)
class CrawlingFailed(Event):
    folder: Folder
    error: Exception


class CrawlingFinished(Event):
    folder: Folder