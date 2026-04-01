from PySide6.QtCore import Signal, QObject

from iteradraw.core.application.shell import ApplicationShell
from iteradraw.core.domain.events.folder_events import FolderAdded, \
    FolderRemoved, FolderSetRenamed, FolderSetDeleted, FolderSetCreated
from iteradraw.core.infrastructure.buses.command_bus import CommandBus
from iteradraw.core.infrastructure.buses.event_bus import EventBus
from iteradraw.interfaces import UnitOfWorkFactory


class PySideShell(ApplicationShell):
    class Signals(QObject):
        folder_added: Signal = Signal(int, str, bool)
        folder_removed: Signal = Signal(int, str)
        folderset_renamed: Signal = Signal(int, str)
        folderset_deleted: Signal = Signal(int)
        folderset_created: Signal = Signal(int)

    def __init__(
            self,
            command_bus: CommandBus,
            event_bus: EventBus,
            uow_factory: UnitOfWorkFactory
    ):
        super().__init__(command_bus, event_bus, uow_factory)
        self.signals = self.Signals()
        self._connect_signals()

    def add_folder(
        self, 
        folderset_id: int, 
        folder_path: str, 
        enabled: bool = True
    ):
        super().add_folder(
            folderset_id=folderset_id,
            folder_path=folder_path,
            enabled=enabled
        )

    def remove_folder(self, folderset_id: int, folder_path: str):
        super().remove_folder(
            folderset_id=folderset_id,
            folder_path=folder_path,
        )

    def rename_folderset(self, folderset_id: int, name: str):
        super().rename_folderset(
            folderset_id=folderset_id,
            name=name,
        )

    def add_folderset(self, name: str):
        super().add_folderset(
            name=name
        )

    def delete_folderset(self, folderset_id: int):
        super().delete_folderset(
            folderset_id=folderset_id,
        )

    def set_folderset_enabled(self, folderset_id: int, folder_path: str,
                              enabled: bool):
        super().set_folderset_enabled(
            folderset_id=folderset_id,
            folder_path= folder_path,
            enabled= enabled,
        )

    def set_all_folders_enabled(self, folderset_id: int, enabled: bool):
        super().set_all_folders_enabled(
            folderset_id=folderset_id,
            enabled= enabled,
        )

    def move_folder(self, origin_id, destination_id, folder_path: str):
        super().move_folder(
            origin_id=origin_id,
            destination_id=destination_id,
            folder_path=folder_path,
        )

    # Pyside signals

    def _connect_signals(self) -> None:
        self.event_bus.subscribe(
            event_type=FolderAdded,
            listener=self._on_folder_added,
        )
        self.event_bus.subscribe(
            event_type=FolderRemoved,
            listener=self._on_folder_removed,
        )
        self.event_bus.subscribe(
            event_type=FolderSetRenamed,
            listener=self._on_folderset_renamed,
        )
        self.event_bus.subscribe(
            event_type=FolderSetDeleted,
            listener=self._on_folderset_deleted,
        )
        self.event_bus.subscribe(
            event_type=FolderSetCreated,
            listener=self._on_folderset_created,
        )

    def _on_folder_added(self, event: FolderAdded):
        self.signals.folder_added.emit(
            event.folderset_id,
            str(event.folder_path),
            event.enabled)

    def _on_folder_removed(self, event: FolderRemoved):
        self.signals.folder_removed.emit(
            event.folderset_id,
            event.folder_path,
        )

    def _on_folderset_deleted(self, event: FolderSetDeleted):
        self.signals.folderset_deleted.emit(
            event.folderset_id
        )

    def _on_folderset_created(self, event: FolderSetCreated):
        self.signals.folderset_created.emit(
            event.folderset_id,
        )

    def _on_folderset_renamed(self, event: FolderSetRenamed):
        self.signals.folderset_renamed.emit(
            event.folderset_id,
            event.name,
        )
