import qt_core as qt
from gui.widgets.terminal import TerminalWidget


class CommandPage(qt.QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName("CommandPage")

        self.theme = theme

        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.label = qt.QLabel("Command")
        self.label.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)

        # self.terminal = TerminalWidget(theme, self)

        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.label)
        # self.layout.addWidget(self.terminal)
