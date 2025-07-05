import qt_core as qt


class TopBar(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)

        bg_color = theme['colors'].get('bar')

        self.setMinimumHeight(20)
        self.setMaximumHeight(20)
        self.setStyleSheet(f"background-color: {bg_color};")

        self.layout = qt.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)


        self.spacer = qt.QSpacerItem(0, 0, qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Minimum)

        self.button_toggle_right_column = qt.QPushButton("Right")

        self.add_layout()

    def add_layout(self):
        self.layout.addSpacerItem(self.spacer)
        self.layout.addWidget(self.button_toggle_right_column)
