from PySide6.QtCore import QObject, Signal

from iteradraw.core.application.shell import ApplicationShell
from iteradraw.core.domain.events.folder_events import FolderAdded
from iteradraw.core.infrastructure.buses.command_bus import CommandBus
from iteradraw.core.infrastructure.buses.event_bus import EventBus


class PySideSignals(QObject):
    folder_added: Signal = Signal(str, str)
    folder_removed: Signal = Signal(str, str)
    folderset_renamed: Signal = Signal(str, str)

class PySideShell(ApplicationShell):
    def __init__(self, command_bus: CommandBus, event_bus: EventBus):
        super().__init__(command_bus, event_bus)

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
        ...

    def remove_folder(self, folderset_id: int, folder_path: str):
        super().remove_folder(
            folderset_id=folderset_id,
            folder_path=folder_path,
        )
        ...

    def rename_folderset(self, folderset_id: int, name: str):
        super().rename_folderset(
            folderset_id=folderset_id,
            name=name,
        )
        ...

    def add_folderset(self, name: str):
        super().add_folderset(
            name=name
        )
        ...

    def delete_folderset(self, folderset_id: int):
        super().delete_folderset(
            folderset_id=folderset_id,
        )
        ...

    def set_folderset_enabled(self, folderset_id: int, folder_path: str,
                              enabled: bool):
        super().set_folderset_enabled(
            folderset_id=folderset_id,
            folder_path= folder_path,
            enabled= enabled,
        )
        ...

    def set_all_folders_enabled(self, folderset_id: int, enabled: bool):
        super().set_all_folders_enabled(
            folderset_id=folderset_id,
            enabled= enabled,
        )
        ...

    def move_folder(self, origin_id, destination_id, folder_path: str):
        super().move_folder(
            origin_id=origin_id,
            destination_id=destination_id,
            folder_path=folder_path,
        )
        ...

    def _connect_signals(self, event_bus: EventBus) -> None:
        ...

    def _on_folder_added(self, event: FolderAdded)
        ...
