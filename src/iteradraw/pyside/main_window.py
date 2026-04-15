from PySide6.QtWidgets import QMainWindow, QFileDialog, QTabWidget

from iteradraw.pyside.pyside_shell import PySideShell
from iteradraw.pyside.views.tabs_views import SlideshowControlTab, SettingsTab


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
        self._build()
        self._configure_window()

    def _build(self):
        self.file_dialog = QFileDialog()
        tabs = QTabWidget()
        main_tab = SlideshowControlTab(
            shell=self.shell,
        )
        settings_tab = SettingsTab()

        # add tabs in display order
        tabs.addTab(settings_tab, "⚙")
        tabs.addTab(main_tab, "Slideshow")

        # define focused tab (index starts at 0, default is first added)
        tabs.setCurrentIndex(1)
        self.setCentralWidget(tabs)

    def _configure_window(self):
        self.setWindowTitle("Showcase: FolderGroupView")
        self.resize(960, 540)
