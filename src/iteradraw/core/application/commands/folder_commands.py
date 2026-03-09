from dataclasses import dataclass
from pathlib import Path

from iteradraw.interfaces import Command

"""
Commands
"""


@dataclass(frozen=True)
class AddFolderCommand(Command):
    folderset_id: int
    folder_path: Path
    enabled: bool


@dataclass(frozen=True)
class RemoveFolderCommand(Command):
    folderset_id: int
    folder_path: Path


@dataclass(frozen=True)
class RenameFolderSetCommand(Command):
    folderset_id: int
    new_name: str


@dataclass(frozen=True)
class AddFolderSetCommand(Command):
    display_name: str


@dataclass(frozen=True)
class DeleteFolderSetCommand(Command):
    folderset_id: int


@dataclass(frozen=True)
class MoveFolderBetweenFolderSetsCommand(Command):
    origin_folderset_id: int
    destination_folderset_id: int
    folder_path: Path


@dataclass(frozen=True)
class SetFolderEnabledCommand(Command):
    folderset_id: int
    folder_path: Path
    target_enabled: bool


@dataclass(frozen=True)
class SetAllFoldersEnabledCommand(Command):
    folderset_id: int
    target_enabled: bool
