from abc import ABC
from pathlib import Path

from iteradraw.core.application.commands.folder_commands import \
    AddFolderCommand, RenameFolderSetCommand, RemoveFolderCommand, \
    SetFolderEnabledCommand, SetAllFoldersEnabledCommand, \
    MoveFolderBetweenFolderSetsCommand, DeleteFolderSetCommand, \
    AddFolderSetCommand
from iteradraw.core.infrastructure.buses.command_bus import CommandBus


class ApplicationShell(ABC):

    def __init__(self, command_bus: CommandBus, ):
        self.command_bus = command_bus

    def start(self):
        pass

    def shutdown(self):
        pass

# Command API

    def next_timed_slide(self):
        raise NotImplementedError

    def previous_timed_slide(self):
        raise NotImplementedError

    def next_slide(self):
        raise NotImplementedError

    def previous_slide(self):
        raise NotImplementedError

# Folder Command Wrappers

    def add_folder(self, folderset_id: int, folder_path: Path, enabled: bool):
        cmd = AddFolderCommand(
            folderset_id=folderset_id,
            folder_path= folder_path,
            enabled= enabled,
        )
        self.command_bus.dispatch(cmd)

    def remove_folder(self, folderset_id: int, folder_path: Path):
        cmd = RemoveFolderCommand(
            folderset_id=folderset_id,
            folder_path=folder_path,
        )
        self.command_bus.dispatch(cmd)

    def rename_folderset(self, folderset_id: int, name: str):
        cmd = RenameFolderSetCommand(
            folderset_id=folderset_id,
            new_name=name,
        )
        self.command_bus.dispatch(cmd)

    def add_folderset(self, name: str):
        cmd = AddFolderSetCommand(
            display_name=name
        )
        self.command_bus.dispatch(cmd)

    def delete_folderset(self, folderset_id: int):
        cmd = DeleteFolderSetCommand(
            folderset_id=folderset_id,
        )
        self.command_bus.dispatch(cmd)

    def set_folderset_enabled(self, folderset_id: int, folder_path: Path, enabled: bool):
        cmd = SetFolderEnabledCommand(
            folderset_id=folderset_id,
            folder_path= folder_path,
            target_enabled= enabled,
        )
        self.command_bus.dispatch(cmd)

    def set_all_folders_enabled(self, folderset_id: int, enabled: bool):
        cmd = SetAllFoldersEnabledCommand(
            folderset_id=folderset_id,
            target_enabled= enabled,
        )
        self.command_bus.dispatch(cmd)

    def move_folder(self, origin_id, destination_id, folder_path: Path):
        cmd = MoveFolderBetweenFolderSetsCommand(
            origin_folderset_id=origin_id,
            destination_folderset_id=destination_id,
            folder_path=folder_path,
        )
        self.command_bus.dispatch(cmd)

# Query API

    def fetch_session_statistics(self):
        raise NotImplementedError

    def fetch_session_images(self):
        raise NotImplementedError

    def fetch_tags(self):
        raise NotImplementedError