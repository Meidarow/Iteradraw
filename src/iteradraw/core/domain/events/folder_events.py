from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from iteradraw.interfaces import Event
from iteradraw.core.domain.models.folder import FolderSet

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
class FolderSetAdded(Event):
    folderset_id: int


@dataclass(frozen=True)
class FolderSetRemoved(Event):
    folderset_id: int


@dataclass(frozen=True)
class FolderSetRenamed(Event):
    folderset_id: int
    new_name: str


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
    origin_folderset_id: int
    destination_folderset_id: int
    folder_path: Path
