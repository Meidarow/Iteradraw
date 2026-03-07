"""
Handlers for all Folder and FolderSet based operations in IteraDraw.
Subclasses of CommandHandler.

Classes:
    AddFolderCommandHandler
    RemoveFolderCommandHandler
    RenameFolderSetCommandHandler
    AddFolderSetCommandHandler
    RemoveFolderSetCommandHandler
    MoveFolderBetweenFolderSetsCommandHandler
    ChangeFolderEnabledCommandHandler
    ChangeAllFoldersEnabledCommandHandler
"""

from iteradraw.core.application.commands.folder_commands import (
    AddFolderCommand,
    RemoveFolderCommand,
    RenameFolderSetCommand,
    DeleteFolderSetCommand,
    AddFolderSetCommand,
    SetFolderEnabledCommand,
    SetAllFoldersEnabledCommand,
    MoveFolderBetweenFolderSetsCommand,
)
from iteradraw.core.domain.events.folder_events import FolderSetRenamed, FolderRemoved, FolderAdded, FolderSetAdded, \
    FolderSetRemoved, FolderEnabledSet, AllFoldersEnabledSet, FolderMovedBetweenFolderSets
from iteradraw.core.infrastructure.buses.event_bus import EventBus
from iteradraw.interfaces import IdGenerator, CommandHandler
from iteradraw.core.domain.models.folder import FolderSet
from iteradraw.core.domain.repositories.folder_repository import FolderRepository


class AddFolderCommandHandler(CommandHandler[AddFolderCommand]):
    command_type = AddFolderCommand
    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def handle(self, command: AddFolderCommand):
        old_folderset = self.folder_repo.get(command.folderset_id)
        new_folderset = old_folderset.add(command.folder_path, command.enabled)
        self.folder_repo.save(folderset=new_folderset)
        evt = FolderAdded(
            folderset_id=command.folderset_id,
            folder_path=command.folder_path,
            enabled=command.enabled,
        )
        self.event_bus.publish(evt)


class RemoveFolderCommandHandler(CommandHandler[RemoveFolderCommand]):
    command_type = RemoveFolderCommand
    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def handle(self, command: RemoveFolderCommand):
        old_folderset = self.folder_repo.get(command.folderset_id)
        new_folderset = old_folderset.remove(command.folder_path)
        self.folder_repo.save(folderset=new_folderset)
        evt = FolderRemoved(
            folderset_id=command.folderset_id, folder_path=command.folder_path
        )
        self.event_bus.publish(evt)

class RenameFolderSetCommandHandler(CommandHandler[RenameFolderSetCommand]):
    command_type = RenameFolderSetCommand
    def __init__(
        self,
        folder_repo: FolderRepository,
        event_bus: EventBus,
    ):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def handle(self, command: RenameFolderSetCommand):
        old_folderset = self.folder_repo.get(command.folderset_id)
        new_folderset = old_folderset.rename(command.new_name)
        self.folder_repo.save(folderset=new_folderset)
        evt = FolderSetRenamed(
            folderset_id=command.folderset_id, new_name=command.new_name
        )
        self.event_bus.publish(evt)


class AddFolderSetCommandHandler(CommandHandler[AddFolderSetCommand]):
    command_type = AddFolderSetCommand
    def __init__(
        self,
        folder_repo: FolderRepository,
        event_bus: EventBus,
        id_generator: IdGenerator,
    ):
        self.folder_repo = folder_repo
        self.event_bus = event_bus
        self.id_generator = id_generator

    def handle(self, command: AddFolderSetCommand):
        new_folderset_id = self.id_generator.generate()
        new_folderset = FolderSet(
            uuid=new_folderset_id, display_name=command.display_name
        )
        self.folder_repo.save(folderset=new_folderset)
        evt = FolderSetAdded(folderset=new_folderset)
        self.event_bus.publish(evt)


class DeleteFolderSetCommandHandler(CommandHandler[DeleteFolderSetCommand]):
    command_type = DeleteFolderSetCommand
    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def handle(self, command: DeleteFolderSetCommand):
        self.folder_repo.remove(folderset_id=command.folderset_id)
        evt = FolderSetRemoved(folderset_id=command.folderset_id)
        self.event_bus.publish(evt)


class SetFolderEnabledCommandHandler(CommandHandler[SetFolderEnabledCommand]):
    command_type = SetFolderEnabledCommand
    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def handle(self, command: SetFolderEnabledCommand):
        folderset = self.folder_repo.get(command.folderset_id)
        new_folderset = folderset.set_folder_enabled(
            path=command.folder_path, enabled=command.target_enabled
        )
        self.folder_repo.save(folderset=new_folderset)
        evt = FolderEnabledSet(
            folderset_id=command.folderset_id,
            folder_path=command.folder_path,
            enabled=command.target_enabled,
        )
        self.event_bus.publish(evt)


class SetAllFoldersEnabledCommandHandler(CommandHandler[SetAllFoldersEnabledCommand]):
    command_type = SetAllFoldersEnabledCommand
    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def handle(self, command: SetAllFoldersEnabledCommand):
        folderset = self.folder_repo.get(command.folderset_id)
        new_folderset = folderset.set_all_folders_enabled(
            enabled=command.target_enabled
        )
        self.folder_repo.save(folderset=new_folderset)
        evt = AllFoldersEnabledSet(
            folderset_id=command.folderset_id, enabled=command.target_enabled
        )
        self.event_bus.publish(evt)


class MoveFolderBetweenFolderSetsCommandHandler(CommandHandler[MoveFolderBetweenFolderSetsCommand]):
    command_type = MoveFolderBetweenFolderSetsCommand
    """
    TODO Planned feature. Not integrated in GUI.
    This handler is already integrated into the DI container.
    Careful here, this requires changing both foldersets AFTER verifying if
    the target FS can receive the folder, that is, doesn't already have it.
    """

    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def handle(self, command: MoveFolderBetweenFolderSetsCommand):
        origin = self.folder_repo.get(command.origin_folderset_id)
        destination = self.folder_repo.get(command.destination_folderset_id)

        folder = origin.folders.get(command.folder_path)
        if not folder or folder.path in destination.folders.keys():
            return

        new_origin = origin.remove(command.folder_path)
        new_destination = destination.add(folder.path, folder.enabled)

        self.folder_repo.save(new_origin)
        self.folder_repo.save(new_destination)
        evt = FolderMovedBetweenFolderSets(
            origin_folderset_id=command.origin_folderset_id,
            destination_folderset_id=command.destination_folderset_id,
            folder_path=command.folder_path,
        )
        self.event_bus.publish(evt)
