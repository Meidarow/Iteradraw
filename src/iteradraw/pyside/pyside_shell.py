from PySide6.QtCore import Signal, QObject

from iteradraw.core.application.shell import ApplicationShell
from iteradraw.core.domain.events.folder_events import FolderAdded, \
    FolderRemoved, FolderSetRenamed, FolderSetDeleted, FolderSetCreated
from iteradraw.core.domain.models.folder import FolderSet


class PySideShell:
    class _Signals(QObject):
        folder_added: Signal = Signal(int, str, bool)
        folder_removed: Signal = Signal(int, str)
        folderset_renamed: Signal = Signal(int, str)
        folderset_deleted: Signal = Signal(int)
        folderset_created: Signal = Signal(int)
        slideshow_prepared: Signal = Signal(bool)
        slideshow_finished: Signal = Signal()  # last session ID for hot-continue

    def __init__(
            self,
            shell: ApplicationShell
    ):
        self._shell = shell
        self.signals = self._Signals()
        self._connect_signals()

    # Command API
    def start_slideshow(self, timer: int, shuffle: bool):
        self.signals.slideshow_prepared.emit(True)
        self._shell.start_slideshow(timer, shuffle)

    def next_timed_slide(self):
        raise NotImplementedError

    def previous_timed_slide(self):
        raise NotImplementedError

    def next_slide(self):
        raise NotImplementedError

    def previous_slide(self):
        raise NotImplementedError

    def add_folder(
        self, 
        folderset_id: int, 
        folder_path: str, 
        enabled: bool = True
    ):
        self._shell.add_folder(
            folderset_id=folderset_id,
            folder_path=folder_path,
            enabled=enabled
        )

    def remove_folder(self, folderset_id: int, folder_path: str):
        self._shell.remove_folder(
            folderset_id=folderset_id,
            folder_path=folder_path,
        )

    def rename_folderset(self, folderset_id: int, name: str):
        self._shell.rename_folderset(
            folderset_id=folderset_id,
            name=name,
        )

    def add_folderset(self, name: str):
        self._shell.add_folderset(
            name=name
        )

    def delete_folderset(self, folderset_id: int):
        self._shell.delete_folderset(
            folderset_id=folderset_id,
        )

    def set_folderset_enabled(self, folderset_id: int, folder_path: str,
                              enabled: bool):
        self._shell.set_folderset_enabled(
            folderset_id=folderset_id,
            folder_path= folder_path,
            enabled= enabled,
        )

    def set_all_folders_enabled(self, folderset_id: int, enabled: bool):
        self._shell.set_all_folders_enabled(
            folderset_id=folderset_id,
            enabled= enabled,
        )

    def move_folder(self, origin_id, destination_id, folder_path: str):
        self._shell.move_folder(
            origin_id=origin_id,
            destination_id=destination_id,
            folder_path=folder_path,
        )

    # Pyside signals

    def _connect_signals(self) -> None:
        self._shell.event_bus.subscribe(
            event_type=FolderAdded,
            listener=self._on_folder_added,
        )
        self._shell.event_bus.subscribe(
            event_type=FolderRemoved,
            listener=self._on_folder_removed,
        )
        self._shell.event_bus.subscribe(
            event_type=FolderSetRenamed,
            listener=self._on_folderset_renamed,
        )
        self._shell.event_bus.subscribe(
            event_type=FolderSetDeleted,
            listener=self._on_folderset_deleted,
        )
        self._shell.event_bus.subscribe(
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
            str(event.folder_path),
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

    # Query API

    def fetch_folderset(self, folderset_id: int) -> FolderSet:
        return self._shell.fetch_folderset(
            folderset_id=folderset_id,
        )

    def fetch_all_foldersets(self) -> list[FolderSet]:
        return self._shell.fetch_all_foldersets()

    def fetch_session_statistics(self):
        raise NotImplementedError

    def fetch_session_images(self):
        raise NotImplementedError

    def fetch_tags(self):
        raise NotImplementedError
