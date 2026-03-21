from dataclasses import dataclass
from pathlib import Path

from iteradraw.interfaces import Command

"""
Commands
"""


@dataclass(frozen=True)
class AddFolderCommand(Command):
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
class RemoveFolderCommand(Command):
    """
    Attributes:
        folderset_id: int
        folder_path: Path
    """
    folderset_id: int
    folder_path: Path


@dataclass(frozen=True)
class RenameFolderSetCommand(Command):
    """
    Attributes:
        folderset_id: int
        new_name: str
    """
    folderset_id: int
    new_name: str


@dataclass(frozen=True)
class AddFolderSetCommand(Command):
    """
    Attributes:
        display_name: str
    """
    display_name: str


@dataclass(frozen=True)
class DeleteFolderSetCommand(Command):
    """
    Attributes:
        folderset_id: int
    """
    folderset_id: int


@dataclass(frozen=True)
class SetFolderEnabledCommand(Command):
    """
    Attributes:
        folderset_id: int
        folder_path: Path
        target_enabled: bool
    """
    folderset_id: int
    folder_path: Path
    target_enabled: bool


@dataclass(frozen=True)
class SetAllFoldersEnabledCommand(Command):
    """
    Attributes:
        folderset_id: int
        target_enabled: bool
    """
    folderset_id: int
    target_enabled: bool


@dataclass(frozen=True)
class MoveFolderBetweenFolderSetsCommand(Command):
    """
    Attributes:
        origin_folderset_id: int
        destination_folderset_id: int
        folder_path: Path
    """
    origin_folderset_id: int
    destination_folderset_id: int
    folder_path: Path