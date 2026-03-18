from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
)

from iteradraw.pyside.pyside_shell import PySideShell
from iteradraw.pyside.views.control_widgets import SidePanelView
from iteradraw.pyside.views.folder_widgets import FolderPanelView


class SlideshowControlTab(QWidget):
    """
    View of the primary tab of Iteradraw.

    Coordinates the segments of the GUI and emits signals.

    Core Segments:
      - Folder Segment: Allows user to view folder/foldergroups, perform
      CRUD ops on them and select/deselect them.
      - Timer Segment: Allows user to add/select timers.
      - Trigger Segment: Presents buttons for the user to trigger app
      behaviors.

    Does NOT handle any data, only UI elements. Data handling is delegated
    to each appropriate data-bound component's viewmodel.
    """

    def __init__(self, shell: PySideShell):
        super().__init__()
        horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
        folder_panel = FolderPanelView(
            shell=shell,
        )
        sidebar_panel = SidePanelView()

        horizontal_splitter.addWidget(folder_panel)
        horizontal_splitter.addWidget(sidebar_panel)
        horizontal_splitter.setStretchFactor(0, 12)
        horizontal_splitter.setStretchFactor(1, 1)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(horizontal_splitter)


class SettingsTab(QWidget):
    """
    Secondary settings tab for Iteradraw.

    Presents a series of settings that can be altered to the user's preference.

    Core Segments:

    """

    ...
