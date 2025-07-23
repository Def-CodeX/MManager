import qt_core as qt


class CommandPage(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName("CommandPage")

        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.label = qt.QLabel("Command")
        self.label.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)

        self.add_widgets()

    def add_widgets(self):
        self.layout.addWidget(self.label)
