from PySide6.QtWidgets import (
    QWidget,
    QGroupBox,
    QFormLayout,
    QCheckBox,
    QSpinBox,
    QPushButton,
)

from iteradraw.pyside.pyside_shell import PySideShell


class SidePanelView(QGroupBox):
    def __init__(self, shell: PySideShell):
        super().__init__()
        self.shell = shell
        self._form = None
        self._build()
        self._bind_signals()

    def _build(self):
        self._form = QFormLayout()

        self._timer_field = QSpinBox()
        self._shuffle_checkbox = QCheckBox()
        self._start_button = QPushButton("Start")

        self._form.addRow("Timer (seconds):", self._timer_field)
        self._form.addRow("Shuffle:", self._shuffle_checkbox)
        self._form.addRow(self._start_button)
        self.setLayout(self._form)

    def _bind_signals(self):
        self._start_button.pressed.connect(lambda: self.shell.start_slideshow(
            timer=self._timer_field.value(),
            shuffle=self._shuffle_checkbox.isChecked()
        ))


class TimerSelectionView(QWidget):
    ...


class TriggerConsoleView(QWidget):
    ...
