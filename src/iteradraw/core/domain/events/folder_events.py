from dataclasses import dataclass
from uuid import UUID

from iteradraw.interfaces import Event
from iteradraw.core.domain.models.folder import FolderSet

@dataclass(frozen=True)
class FolderAdded(Event):
    folderset_id: UUID
    folder_path: str
    enabled: bool


@dataclass(frozen=True)
class FolderRemoved(Event):
    folderset_id: UUID
    folder_path: str


@dataclass(frozen=True)
class FolderSetAdded(Event):
    folderset: FolderSet


@dataclass(frozen=True)
class FolderSetRemoved(Event):
    folderset_id: UUID


@dataclass(frozen=True)
class FolderSetRenamed(Event):
    folderset_id: UUID
    new_name: str


@dataclass(frozen=True)
class FolderEnabledSet(Event):
    folderset_id: UUID
    folder_path: str
    enabled: bool


@dataclass(frozen=True)
class AllFoldersEnabledSet(Event):
    folderset_id: UUID
    enabled: bool


@dataclass(frozen=True)
class FolderMovedBetweenFolderSets(Event):
    origin_folderset_id: UUID
    destination_folderset_id: UUID
    folder_path: str
