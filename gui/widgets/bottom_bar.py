import qt_core as qt


class BottomBar(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)

        bg_color = theme['colors'].get('bar')

        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
        self.setStyleSheet(f"background-color: {bg_color};")