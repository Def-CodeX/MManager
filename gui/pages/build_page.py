import qt_core as qt


class BuildPage(qt.QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName("BuildPage")

        self.theme = theme

        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.label = qt.QLabel("Build")
        self.label.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)

        self.add_widgets()

    def add_widgets(self):
        self.layout.addWidget(self.label)
