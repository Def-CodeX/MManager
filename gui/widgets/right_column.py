import qt_core as qt


class RightColumn(qt.QFrame):
    def __init__(self, theme, parent=None):
        super().__init__(parent)

        bg_color = theme['colors'].get('column')
        border_color = theme['colors'].get('shadow')

        self.setMinimumWidth(0)
        self.setMaximumWidth(0)
        self.setStyleSheet(f"background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 10px;")