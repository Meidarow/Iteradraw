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
from iteradraw.core.domain.events.folder_events import FolderSetRenamed, \
    FolderRemoved, FolderAdded, FolderSetCreated, \
    FolderSetDeleted, FolderEnabledSet, AllFoldersEnabledSet, \
    FolderMovedBetweenFolderSets
from iteradraw.core.infrastructure.buses.event_bus import EventBus
from iteradraw.interfaces import CommandHandler, UnitOfWorkFactory


class AddFolderCommandHandler(CommandHandler[AddFolderCommand]):
    """
    Attributes:
        command_type: AddFolderCommand

    Arguments:
        uow_factory: UnitOfWorkFactory
        event_bus: EventBus
    """
    command_type = AddFolderCommand

    def __init__(self, uow_factory: UnitOfWorkFactory, event_bus: EventBus,
                 **_):
        self.uow_factory = uow_factory
        self.event_bus = event_bus

    def handle(self, command: AddFolderCommand):
        with self.uow_factory() as uow:
            folderset = uow.folder_repo.get_folderset(
                folderset_id=command.folderset_id
            )
            uow.dir_repo.create_directories([command.folder_path])
            folderset = folderset.add(command.folder_path, command.enabled)
            uow.folder_repo.update_folderset_folders(folderset=folderset)
            uow.commit()

        evt = FolderAdded(
            folderset_id=command.folderset_id,
            folder_path=command.folder_path,
            enabled=command.enabled,
        )
        self.event_bus.publish(evt)


class RemoveFolderCommandHandler(CommandHandler[RemoveFolderCommand]):
    """
    Attributes:
        command_type: RemoveFolderCommand

    Arguments:
        uow_factory: UnitOfWorkFactory
        event_bus: EventBus
    """
    command_type = RemoveFolderCommand

    def __init__(self, uow_factory: UnitOfWorkFactory, event_bus: EventBus,
                 **_):
        self.uow_factory = uow_factory
        self.event_bus = event_bus

    def handle(self, command: RemoveFolderCommand):
        with self.uow_factory() as uow:
            folderset = uow.folder_repo.get_folderset(command.folderset_id)
            folderset = folderset.remove(command.folder_path)
            uow.folder_repo.update_folderset_folders(folderset=folderset)
            uow.commit()

        evt = FolderRemoved(
            folderset_id=command.folderset_id,
            folder_path=command.folder_path
        )
        self.event_bus.publish(evt)

class RenameFolderSetCommandHandler(CommandHandler[RenameFolderSetCommand]):
    """
    Attributes:
        command_type: RenameFolderSetCommand

    Arguments:
        uow_factory: UnitOfWorkFactory
        event_bus: EventBus
    """
    command_type = RenameFolderSetCommand

    def __init__(self, uow_factory: UnitOfWorkFactory, event_bus: EventBus,
                 **_):
        self.uow_factory = uow_factory
        self.event_bus = event_bus

    def handle(self, command: RenameFolderSetCommand):
        with self.uow_factory() as uow:
            folderset = uow.folder_repo.get_folderset(command.folderset_id)
            folderset = folderset.rename(command.new_name)
            uow.folder_repo.update_folderset_name(folderset=folderset)
            uow.commit()

        evt = FolderSetRenamed(
            folderset_id=command.folderset_id,
            name=command.new_name
        )
        self.event_bus.publish(evt)


class AddFolderSetCommandHandler(CommandHandler[AddFolderSetCommand]):
    """
    Attributes:
        command_type: AddFolderSetCommand

    Arguments:
        uow_factory: UnitOfWorkFactory
        event_bus: EventBus
    """
    command_type = AddFolderSetCommand

    def __init__(self, uow_factory: UnitOfWorkFactory, event_bus: EventBus,
                 **_):
        self.uow_factory = uow_factory
        self.event_bus = event_bus

    def handle(self, command: AddFolderSetCommand):
        with self.uow_factory() as uow:
            folderset_id = uow.folder_repo.create_folderset(
                folderset_name=command.display_name
            )
            uow.commit()

        evt = FolderSetCreated(
            folderset_id=folderset_id
        )
        self.event_bus.publish(evt)


class DeleteFolderSetCommandHandler(CommandHandler[DeleteFolderSetCommand]):
    """
    Attributes:
        command_type: DeleteFolderSetCommand

    Arguments:
        uow_factory: UnitOfWorkFactory
        event_bus: EventBus
    """
    command_type = DeleteFolderSetCommand

    def __init__(self, uow_factory: UnitOfWorkFactory, event_bus: EventBus,
                 **_):
        self.uow_factory = uow_factory
        self.event_bus = event_bus

    def handle(self, command: DeleteFolderSetCommand):
        with self.uow_factory() as uow:
            uow.folder_repo.delete_folderset(folderset_id=command.folderset_id)
            uow.commit()

        evt = FolderSetDeleted(
            folderset_id=command.folderset_id
        )
        self.event_bus.publish(evt)


class SetFolderEnabledCommandHandler(CommandHandler[SetFolderEnabledCommand]):
    """
    Attributes:
        command_type: SetFolderEnabledCommand

    Arguments:
        uow_factory: UnitOfWorkFactory
        event_bus: EventBus
    """
    command_type = SetFolderEnabledCommand

    def __init__(self, uow_factory: UnitOfWorkFactory, event_bus: EventBus,
                 **_):
        self.uow_factory = uow_factory
        self.event_bus = event_bus

    def handle(self, command: SetFolderEnabledCommand):
        with self.uow_factory() as uow:
            folderset = uow.folder_repo.get_folderset(command.folderset_id)
            folderset = folderset.set_folder_enabled(
                path=command.folder_path,
                enabled=command.target_enabled
            )
            uow.folder_repo.update_folderset_folders(folderset=folderset)
            uow.commit()

        evt = FolderEnabledSet(
            folderset_id=command.folderset_id,
            folder_path=command.folder_path,
            enabled=command.target_enabled,
        )
        self.event_bus.publish(evt)


class SetAllFoldersEnabledCommandHandler(CommandHandler[SetAllFoldersEnabledCommand]):
    """
    Attributes:
        command_type: SetAllFoldersEnabledCommand

    Arguments:
        uow_factory: UnitOfWorkFactory
        event_bus: EventBus
    """
    command_type = SetAllFoldersEnabledCommand

    def __init__(self, uow_factory: UnitOfWorkFactory, event_bus: EventBus,
                 **_):
        self.uow_factory = uow_factory
        self.event_bus = event_bus

    def handle(self, command: SetAllFoldersEnabledCommand):
        with self.uow_factory() as uow:
            folderset = uow.folder_repo.get_folderset(command.folderset_id)
            new_folderset = folderset.set_all_folders_enabled(
                enabled=command.target_enabled
            )
            uow.folder_repo.update_folderset_folders(folderset=new_folderset)
            uow.commit()

        evt = AllFoldersEnabledSet(
            folderset_id=command.folderset_id,
            enabled=command.target_enabled
        )
        self.event_bus.publish(evt)


class MoveFolderBetweenFolderSetsCommandHandler(CommandHandler[MoveFolderBetweenFolderSetsCommand]):
    """
    TODO Planned feature. Not integrated in GUI.
    This handler is already integrated into the DI container.
    Careful here, this requires changing both foldersets AFTER verifying if
    the target FS can receive the folder, that is, doesn't already have it.

    Currently, in the case that the destination FS has already the transferred
    folder, it simply updates its enabled status to match what the folder had in
    the origin FS.

    Attributes:
        command_type: MoveFolderBetweenFolderSetsCommand

    Arguments:
        uow_factory: UnitOfWorkFactory
        event_bus: EventBus

    Raises:
        KeyError: If origin folderset does not contain the folder being
        transferred.
    """
    command_type = MoveFolderBetweenFolderSetsCommand

    def __init__(self, uow_factory: UnitOfWorkFactory, event_bus: EventBus,
                 **_):
        self.uow_factory = uow_factory
        self.event_bus = event_bus

    def handle(self, command: MoveFolderBetweenFolderSetsCommand):
        with self.uow_factory() as uow:
            origin = uow.folder_repo.get_folderset(command.origin_folderset_id)
            destination = uow.folder_repo.get_folderset(command.destination_folderset_id)

            folder = origin.folders.get(command.folder_path, None)
            if folder is None:
                raise KeyError("Folder not in origin FolderSet")

            origin = origin.remove(command.folder_path)
            destination = destination.add(folder.path, folder.enabled)

            uow.folder_repo.update_folderset_folders(origin)
            uow.folder_repo.update_folderset_folders(destination)
            uow.commit()

        evt = FolderMovedBetweenFolderSets(
            origin_id=command.origin_folderset_id,
            destination_id=command.destination_folderset_id,
            folder_path=command.folder_path,
        )
        self.event_bus.publish(evt)

