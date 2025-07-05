import qt_core as qt


class LeftMenu(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.animation = None
        bg_color = theme['colors'].get('panel')

        self.setMinimumWidth(50)
        self.setMaximumWidth(50)
        self.setStyleSheet(f"background-color: {bg_color};")
        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.button_toggle_menu = qt.QPushButton("Toggle")

        self.spacer = qt.QSpacerItem(0, 0, qt.QSizePolicy.Policy.Minimum, qt.QSizePolicy.Policy.Expanding)

        self.button_toggle_left_column = qt.QPushButton("Left")

        self.add_layout()

    def add_layout(self):
        self.layout.addWidget(self.button_toggle_menu)
        self.layout.addSpacerItem(self.spacer)
        self.layout.addWidget(self.button_toggle_left_column)
