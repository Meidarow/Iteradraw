from dataclasses import dataclass
from pathlib import Path

from iteradraw.interfaces import Event


@dataclass(frozen=True)
class FolderAdded(Event):
    """
    Attributes:
        folderset_id: int
        folder_path: Path
        enabled: bool
    """
    folderset_id: int
    folder_path: Path
    enabled: bool


@dataclass(frozen=True)
class FolderRemoved(Event):
    """
    Attributes:
        folderset_id: int
        folder_path: Path
    """
    folderset_id: int
    folder_path: Path


@dataclass(frozen=True)
class FolderSetCreated(Event):
    """
    Attributes:
        folderset_id: int
    """
    folderset_id: int


@dataclass(frozen=True)
class FolderSetDeleted(Event):
    """
    Attributes:
        folderset_id: int
    """
    folderset_id: int


@dataclass(frozen=True)
class FolderSetRenamed(Event):
    """
    Attributes:
        folderset_id: int
        name: str
    """
    folderset_id: int
    name: str


@dataclass(frozen=True)
class FolderEnabledSet(Event):
    """
    Attributes:
        folderset_id: int
        folder_path: Path
        enabled: bool
    """
    folderset_id: int
    folder_path: Path
    enabled: bool


@dataclass(frozen=True)
class AllFoldersEnabledSet(Event):
    """
    Attributes:
        folderset_id: int
        enabled: bool
    """
    folderset_id: int
    enabled: bool


@dataclass(frozen=True)
class FolderMovedBetweenFolderSets(Event):
    """
    Attributes:
        origin_id: int
        destination_id: int
        folder_path: Path
    """
    origin_id: int
    destination_id: int
    folder_path: Path
