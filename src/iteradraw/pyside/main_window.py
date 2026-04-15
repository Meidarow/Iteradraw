from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow, QFileDialog, QTabWidget, \
    QStackedLayout, QWidget

from iteradraw.pyside.pyside_shell import PySideShell
from iteradraw.pyside.views.slideshow_widgets import ImageViewerWidget
from iteradraw.pyside.views.tabs_views import (SlideshowControlTab,
                                               SettingsTab)


class MainWindow(QMainWindow):
    """
    Top level window of Iteradraw.

    Singular window created by Iteradraw, except dialog windows.

    Core Tabs:
        - MainTab: Slideshow parameter and start-up tab. ID: 1
        - SettingsTab: User preference config window. ID: 0
        - Streak (TBD): Tracks user study time/streak. ID: X

    Window Stack:
        - MainWindow: User navigable for parameters, settings, etc. ID: 0
        - ImageViewer: Slideshow Window "takes over" UI. ID: 1

    Methods:
        - initialize(): Initial boot-up and data load for the app.
    """

    def __init__(self, shell: PySideShell):
        super().__init__()
        self.shell = shell
        self.file_dialog = None
        self.container = QWidget()
        self._build()
        self._configure_window()
        self._bind_signals()

    def _build(self):
        self.setCentralWidget(self.container)
        self.file_dialog = QFileDialog()
        self.tabs = QTabWidget(self)
        self.tabs.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding)
        main_tab = SlideshowControlTab(shell=self.shell)
        settings_tab = SettingsTab()

        self.screens = QStackedLayout(self)
        image_viewer = ImageViewerWidget(self, self.shell)

        # placeholder for testing
        image_viewer.set_image("/Users/gabriel/Desktop/testimages/0004.jpg")

        self.screens.insertWidget(0, self.tabs)
        self.screens.insertWidget(1, image_viewer)

        self.screens.setCurrentIndex(0)

        # add self.tabs in display order
        self.tabs.addTab(settings_tab, "⚙")
        self.tabs.addTab(main_tab, "Slideshow")

        # define focused tab (index starts at 0, default is first added)
        self.tabs.setCurrentIndex(1)
        self.container.setLayout(self.screens)

    def _configure_window(self):
        self.setWindowTitle("Showcase: FolderGroupView")
        self.resize(960, 540)

    def _bind_signals(self):
        self.shell.signals.slideshow_prepared.connect(self.show_slideshow)
        self.shell.signals.slideshow_finished.connect(self.hide_slideshow)

    def show_slideshow(self):
        self.screens.setCurrentIndex(1)

    def hide_slideshow(self):
        self.screens.setCurrentIndex(0)
