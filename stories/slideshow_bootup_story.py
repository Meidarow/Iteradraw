import sys

from typing import Optional
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QStackedLayout, QFormLayout, QPushButton, QWidget

# 2. Import the REAL commands and events your view uses
from iteradraw.core.application.commands.slideshow_commands import StartSlideshowCommand

# 1. Import your REAL buses
from iteradraw.core.infrastructure import CommandBus
from iteradraw.pyside import ImageViewerWidget


class SidePanelView(QWidget):
    def __init__(self, command_bus: Optional[CommandBus], parent=None):
        super().__init__()
        form = QFormLayout()
        self.command_bus = command_bus
        button = QPushButton("Start")
        button.pressed.connect(self._start_slideshow)
        form.addRow(button)
        self.setLayout(form)

    def _start_slideshow(self):
        cmd = StartSlideshowCommand()
        self.command_bus.dispatch(cmd)

class ProtoWindow(QWidget):
    def __init__(self, command_bus: Optional[CommandBus] = None):
        super().__init__()
        self.setWindowTitle("Proto")
        self.setMinimumSize(QSize(800, 600))
        self._layout = QStackedLayout(self)
        self._layout.insertWidget(0, SidePanelView(command_bus))
        image_viewer = ImageViewerWidget(self)
        image_viewer.set_image("/Users/gabriel/Desktop/testimages/0004.jpg")
        self._layout.insertWidget(1, image_viewer)
        self._layout.setCurrentIndex(0)
        self.command_bus = command_bus
        self.command_bus.register(StartSlideshowCommand, self.swap_screen)

    def swap_screen(self, cmd: StartSlideshowCommand):
        self._layout.setCurrentIndex(1)


def main():
    # Set up the Qt Application
    app = QApplication(sys.argv)

    try:
        with open("/home/study/Draw-This/assets/main.qss", "r") as f:
            qss_string = f.read()
            app.setStyleSheet(qss_string)
    except FileNotFoundError:
        print("WARNING: main.qss not found. Using default styles.")

    command_bus = CommandBus()

    # 4. Inject the REAL (but locally-wired) buses
    window = ProtoWindow(command_bus)

    # Run the app
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
