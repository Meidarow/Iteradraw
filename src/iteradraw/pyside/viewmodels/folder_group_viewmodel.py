from PySide6.QtCore import Slot
from PySide6.QtGui import (
    QStandardItemModel,
    QStandardItem,
    Qt,
    QDesktopServices,
)
from PySide6.QtWidgets import QFileDialog, QInputDialog

from iteradraw.pyside.pyside_shell import PySideShell

"""
Viewmodel for the FolderGroupView GUI component.
"""

class FolderGroupViewModel(QStandardItemModel):
    def __init__(self, shell: PySideShell, parent):
        super().__init__(parent)
        self.view = parent
        self.shell = shell
        self.is_handling_change = False
        self.bind_signals()

    def populate(self, folderset) -> None:
        self.itemChanged.disconnect(self.on_checkbox_changed)
        group = FolderGroupItem(
            folderset_id=folderset.id, group_name=folderset.display_name
        )
        self.invisibleRootItem().appendRow(group)
        for f in folderset.all:
            item = FolderItem(str(f.path), f.enabled)
            group.appendRow(item)
        group.setCheckState(self._calculate_state_for_parent(parent=group))
        self.itemChanged.connect(self.on_checkbox_changed)

    def bind_signals(self) -> None:
        self.itemChanged.connect(self.on_checkbox_changed)
        self.shell.signals.folder_added.connect(
            self.on_folder_added_to_folderset)
        self.shell.signals.folderset_renamed.connect(self.on_folderset_renamed)
        self.shell.signals.folder_removed.connect(
            self.on_folder_removed_from_folderset
        )

    # =========================================================================
    # Signal Slots
    #    Slots for Qt-based signals emitted by the GUI.
    #    These allow he GUI to communicate commands to the core.
    #
    # Naming convention:
    #    on_"command"() -> command describes GUI action
    # =========================================================================

    @Slot()
    def on_add_folder_to_group(self) -> None:
        """ """
        parent_item = self.invisibleRootItem().child(0)
        index = parent_item.index()
        folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
        folder_path = QFileDialog().getExistingDirectory()
        if folder_path:
            self.shell.add_folder(folderset_id, folder_path)

    @Slot()
    def on_open_folder_from_group(self, item) -> None:
        QDesktopServices.openUrl(item.text())

    @Slot()
    def on_remove_folder_from_group(self, item) -> None:
        if self._confirm_delete(
            "Would you like to remove this folder from this group?"
        ):
            parent_item = self.invisibleRootItem().child(0)
            index = parent_item.index()
            folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
            folder_path = item.text()
            self.shell.remove_folder(folderset_id, folder_path)

    @Slot()
    def on_rename_folder_group(self) -> None:
        parent_item = self.invisibleRootItem().child(0)
        index = parent_item.index()
        folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
        name, ok = QInputDialog().getText(self.view, "New name:", "")
        if name and ok:
            self.shell.rename_folderset(folderset_id, name)

    @Slot()
    def on_delete_folder_group(self) -> None:
        if self._confirm_delete(
            "Would you like to permanently delete this group?"
        ):
            parent_item = self.invisibleRootItem().child(0)
            index = parent_item.index()
            folderset_id = self.data(index, Qt.ItemDataRole.UserRole)
            self.shell.delete_folderset(folderset_id=folderset_id)

    @Slot()
    def on_checkbox_changed(self, item: QStandardItem) -> None:
        """
        Slot for itemChanged signal.

        Behavior:
            -Evaluates whether checkbox belogns to parent or child widget.
                -Parent: aligns all children to parent new state.
                -Child: evaluates new parent state based on all siblings.
        """
        if self.is_handling_change:
            return
        self.is_handling_change = True
        try:
            if isinstance(item, FolderGroupItem):
                new_state = item.checkState()
                self._set_state_for_all_children(
                    parent_item=item,
                    check_state=new_state,
                )
                self.shell.set_all_folders_enabled(
                    folderset_id=item.data(Qt.ItemDataRole.UserRole),
                    enabled=(Qt.CheckState.Checked == new_state),
                )
            else:
                parent = item.parent()
                new_state = self._calculate_state_for_parent(parent=parent)
                parent.setCheckState(new_state)
                self.shell.set_folderset_enabled(
                    folderset_id=parent.data(Qt.ItemDataRole.UserRole),
                    folder_path=item.text(),
                    enabled=(Qt.CheckState.Checked == item.checkState()),
                )
        finally:
            self.is_handling_change = False

    # =========================================================================
    # Event Signal Slots:
    #    Slots for events issued in the core, emitted as signals in Shell.
    #    These allow the UI to react to core changes.
    #
    # Naming convention:
    #    on_"event_that_happened"() -> event describes past happening
    # =========================================================================

    @Slot()
    def on_folder_added_to_folderset(
            self,
            folder_path: str,
            enabled: bool) -> None:
        parent_item = self.invisibleRootItem().child(0)
        parent_item.appendRow(
            FolderItem(
                folder_path,
                enabled
            ))

    @Slot()
    def on_folder_removed_from_folderset(self, folder_path: str) -> None:
        parent_item = self.invisibleRootItem().child(0)
        for child_row in range(parent_item.rowCount()):
            child_item = parent_item.child(child_row)
            if not child_item.text() == folder_path:
                continue
            parent_item.removeRow(child_row)
            return

    @Slot()
    def on_folderset_renamed(self, name: str) -> None:
        parent_item = self.invisibleRootItem().child(0)
        parent_item.setText(name)

    # =========================================================================
    # Private Helpers
    # =========================================================================

    @staticmethod
    def _set_state_for_all_children(
        parent_item: QStandardItem, check_state: Qt.CheckState
    ) -> None:
        for child_row in range(parent_item.rowCount()):
            child = parent_item.child(child_row)
            child.setCheckState(check_state)

    @staticmethod
    def _calculate_state_for_parent(parent: QStandardItem) -> Qt.CheckState:
        checked_count = 0
        total_children = parent.rowCount()

        for i in range(total_children):
            if parent.child(i).checkState() == Qt.CheckState.Checked:
                checked_count += 1

        if checked_count == 0:
            return Qt.CheckState.Unchecked
        elif checked_count == total_children:
            return Qt.CheckState.Checked
        else:
            return Qt.CheckState.PartiallyChecked

    def _confirm_delete(self, message: str) -> bool:
        """
        Reusable helper to show a "Yes/No" confirmation dialog.
        Returns True if the user clicks Yes, False otherwise.
        """
        from PySide6.QtWidgets import QMessageBox  # Keep import local

        reply = QMessageBox.question(
            self.view,
            "Confirm Delete",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes


class FolderGroupItem(QStandardItem):
    def __init__(self, folderset_id, group_name):
        super().__init__(group_name)
        self.setDropEnabled(True)
        self.setDragEnabled(False)
        self.setCheckable(True)
        self.setAutoTristate(True)
        self.setEditable(False)
        self.setData(
            folderset_id,
            Qt.ItemDataRole.UserRole,
        )


class FolderItem(QStandardItem):
    def __init__(self, folder_path: str, enabled: bool):
        super().__init__(folder_path)
        self.setDropEnabled(False)
        self.setDragEnabled(True)
        self.setCheckable(True)
        self.setEditable(False)
        self.setCheckState(
            Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked
        )
