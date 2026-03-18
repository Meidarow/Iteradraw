from dataclasses import dataclass
from pathlib import Path

from iteradraw.interfaces import Event


@dataclass(frozen=True)
class FolderAdded(Event):
    folderset_id: int
    folder_path: Path
    enabled: bool


@dataclass(frozen=True)
class FolderRemoved(Event):
    folderset_id: int
    folder_path: Path


@dataclass(frozen=True)
class FolderSetCreated(Event):
    folderset_id: int


@dataclass(frozen=True)
class FolderSetDeleted(Event):
    folderset_id: int


@dataclass(frozen=True)
class FolderSetRenamed(Event):
    folderset_id: int
    name: str


@dataclass(frozen=True)
class FolderEnabledSet(Event):
    folderset_id: int
    folder_path: Path
    enabled: bool


@dataclass(frozen=True)
class AllFoldersEnabledSet(Event):
    folderset_id: int
    enabled: bool


@dataclass(frozen=True)
class FolderMovedBetweenFolderSets(Event):
    origin_id: int
    destination_id: int
    folder_path: Path
