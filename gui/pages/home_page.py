import qt_core as qt


class HomePage(qt.QWidget):
    def __init__(self):
        super().__init__()
        if not self.objectName():
            self.setObjectName("HomePage")

        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.label = qt.QLabel("Home")
        self.label.setAlignment(qt.Qt.AlignmentFlag.AlignCenter)

        self.add_widgets()

    def add_widgets(self):
        self.layout.addWidget(self.label)
